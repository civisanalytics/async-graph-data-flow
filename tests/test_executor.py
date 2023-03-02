import asyncio
import time

import pytest

from async_graph_data_flow import AsyncGraph, AsyncExecutor


class TestAsyncExecutorInit:
    def test_init_invalid_graph_instance(self):
        with pytest.raises(TypeError) as excinfo:
            AsyncExecutor(graph=None)
        assert "must be an AsyncGraph instance" in str(excinfo)

    def test_init_with_non_graph_async_node(self):
        async def async_node():
            yield "hello"

        def non_async_node():
            yield "hello"

        etl_graph_instance = AsyncGraph()
        etl_graph_instance.add_node(async_node)

        with pytest.raises(TypeError) as excinfo:
            etl_graph_instance.add_node(non_async_node)
        assert "isn't an async generator function" in str(excinfo.value)

    def test_init_with_valid_graph_async_node(self):
        async def async_node1():
            yield "hello"

        async def async_node2():
            yield "hello"

        etl_graph_instance = AsyncGraph()
        etl_graph_instance.add_node(async_node1)
        etl_graph_instance.add_node(async_node2)

        executor = AsyncExecutor(graph=etl_graph_instance)
        assert executor.graph == etl_graph_instance


def test_async_executor_linear():
    async def extract():
        yield "hello"
        yield "world"

    async def transform(data):
        yield str.title(data)

    async def load():
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(extract)
    etl_graph.add_node(transform)
    etl_graph.add_node(load)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()

    assert etl_executor.data_flow_stats["extract"].get("in") == 0
    assert etl_executor.data_flow_stats["extract"].get("out") == 2
    assert etl_executor.data_flow_stats["extract"].get("err") == 0

    assert etl_executor.data_flow_stats["transform"].get("in") == 2
    assert etl_executor.data_flow_stats["transform"].get("out") == 2
    assert etl_executor.data_flow_stats["transform"].get("err") == 0

    assert etl_executor.data_flow_stats["load"].get("in") == 2
    assert etl_executor.data_flow_stats["load"].get("out") == 2
    assert etl_executor.data_flow_stats["load"].get("err") == 0


def test_async_executor_linear_with_exception_with_halt():
    async def extract():
        yield "data1"
        yield "data2"
        yield "data3"
        yield "data4"
        yield "data5"

    async def transform(data):
        yield str.title(data)

    async def load(data):
        if data in ["Data3", "Data5"]:
            await asyncio.sleep(0)
            raise Exception(f"intentional error for {data}")
        yield data

    async def output():
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(extract)
    etl_graph.add_node(transform)
    etl_graph.add_node(load, halt_on_exception=True)
    etl_graph.add_node(output)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")
    etl_graph.add_edge("load", "output")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()

    assert etl_executor.data_flow_stats["extract"].get("in") == 0
    assert etl_executor.data_flow_stats["extract"].get("out") == 5
    assert etl_executor.data_flow_stats["extract"].get("err") == 0

    assert etl_executor.data_flow_stats["transform"].get("in") == 5
    assert etl_executor.data_flow_stats["transform"].get("out") == 5
    assert etl_executor.data_flow_stats["transform"].get("err") == 0

    assert etl_executor.data_flow_stats["load"].get("in") == 5
    assert etl_executor.data_flow_stats["load"].get("out") == 2
    assert etl_executor.data_flow_stats["load"].get("err") == 1

    assert etl_executor.data_flow_stats["output"].get("in") == 2
    assert etl_executor.data_flow_stats["output"].get("out") == 2
    assert etl_executor.data_flow_stats["output"].get("err") == 0


def test_async_executor_linear_with_exception_without_halt():
    async def extract():
        yield "data1"
        yield "data2"
        yield "data3"
        yield "data4"
        yield "data5"

    async def transform(data):
        yield str.title(data)

    async def load(data):
        if data in ["Data3", "Data5"]:
            await asyncio.sleep(0)
            raise Exception(f"intentional error for {data}")
        yield data

    async def output():
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(extract)
    etl_graph.add_node(transform)
    etl_graph.add_node(load, halt_on_exception=False)
    etl_graph.add_node(output)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")
    etl_graph.add_edge("load", "output")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()

    assert etl_executor.data_flow_stats["extract"].get("in") == 0
    assert etl_executor.data_flow_stats["extract"].get("out") == 5
    assert etl_executor.data_flow_stats["extract"].get("err") == 0

    assert etl_executor.data_flow_stats["transform"].get("in") == 5
    assert etl_executor.data_flow_stats["transform"].get("out") == 5
    assert etl_executor.data_flow_stats["transform"].get("err") == 0

    assert etl_executor.data_flow_stats["load"].get("in") == 5
    assert etl_executor.data_flow_stats["load"].get("out") == 3
    assert etl_executor.data_flow_stats["load"].get("err") == 2

    assert etl_executor.data_flow_stats["output"].get("in") == 3
    assert etl_executor.data_flow_stats["output"].get("out") == 3
    assert etl_executor.data_flow_stats["output"].get("err") == 0


def test_async_executor_nonlinear_with_external_sync_call():
    async def extract():
        yield "hello"
        yield "world"

    async def transform(data):
        await asyncio.sleep(2)
        yield str.title(data)

    async def load1(data):
        for i in range(0, 3):
            await asyncio.sleep(1)
            yield f"load1.{data} {i}"

    async def load2(data):
        cloop = asyncio.get_running_loop()
        for i in range(0, 3):
            await cloop.run_in_executor(None, time.sleep, 1)
            yield f"load2.{data} {i}"

    async def output():
        yield

    etl_graph = AsyncGraph(halt_on_exception=True)
    etl_graph.add_node(extract)
    etl_graph.add_node(transform)
    etl_graph.add_node(load1)
    etl_graph.add_node(load2)
    etl_graph.add_node(output)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load1")
    etl_graph.add_edge("transform", "load2")
    etl_graph.add_edge("load1", "output")
    etl_graph.add_edge("load2", "output")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()

    assert etl_executor.data_flow_stats["extract"].get("in") == 0
    assert etl_executor.data_flow_stats["extract"].get("out") == 2
    assert etl_executor.data_flow_stats["extract"].get("err") == 0

    assert etl_executor.data_flow_stats["transform"].get("in") == 2
    assert etl_executor.data_flow_stats["transform"].get("out") == 2
    assert etl_executor.data_flow_stats["transform"].get("err") == 0

    assert etl_executor.data_flow_stats["load1"].get("in") == 2
    assert etl_executor.data_flow_stats["load1"].get("out") == 6
    assert etl_executor.data_flow_stats["load1"].get("err") == 0

    assert etl_executor.data_flow_stats["load2"].get("in") == 2
    assert etl_executor.data_flow_stats["load2"].get("out") == 6
    assert etl_executor.data_flow_stats["load2"].get("err") == 0

    assert etl_executor.data_flow_stats["output"].get("in") == 12
    assert etl_executor.data_flow_stats["output"].get("out") == 12
    assert etl_executor.data_flow_stats["output"].get("err") == 0


def test_async_executor_with_different_start_node():
    async def node1():
        yield "hello"
        yield "world"

    async def node2(data):
        print(f"Transformer received: {data}")
        yield "data1"
        yield "data2"

    async def node3(data):
        print(f"Data in Load: {data}")
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2, unpack_input=False)
    etl_graph.add_node(node3)
    etl_graph.add_edge("node1", "node2")
    etl_graph.add_edge("node2", "node3")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute(start_nodes={"node2": tuple()})

    assert etl_executor.data_flow_stats["node1"].get("in") == 0
    assert etl_executor.data_flow_stats["node1"].get("out") == 0
    assert etl_executor.data_flow_stats["node1"].get("err") == 0

    assert etl_executor.data_flow_stats["node2"].get("in") == 0
    assert etl_executor.data_flow_stats["node2"].get("out") == 2
    assert etl_executor.data_flow_stats["node2"].get("err") == 0

    assert etl_executor.data_flow_stats["node3"].get("in") == 2
    assert etl_executor.data_flow_stats["node3"].get("out") == 2
    assert etl_executor.data_flow_stats["node3"].get("err") == 0


def test_async_executor_with_unknown_start_node():
    async def node1():
        yield "hello"
        yield "world"

    async def node2(data):
        print(f"Transformer received: {data}")
        yield "data1"
        yield "data2"

    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    with pytest.raises(ValueError) as excinfo:
        etl_executor.execute(start_nodes={"node3": tuple()})
    assert "The graph doesn't have the node 'node3'" in str(excinfo.value)


def test_yielding_a_dict_to_unpack():
    async def node1():
        yield {"foo": 1, "bar": 2}
        yield {"foo": 3, "bar": 4}

    async def node2(bar, foo):  # Ordering of `bar` then `foo` is intentional
        assert foo in (1, 3)
        assert bar in (2, 4)
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()


def test_yielding_a_dict_no_packing():
    async def node1():
        yield {"foo": 1, "bar": 2}
        yield {"foo": 3, "bar": 4}

    async def node2(bar, foo=None):
        assert bar in ({"foo": 1, "bar": 2}, {"foo": 3, "bar": 4})
        assert foo is None
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2, unpack_input=False)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()


def test_yielding_a_dict_but_not_enough_values():
    async def node1():
        yield {"foo": 1, "bar": 2}
        yield {"foo": 3, "bar": 4}

    async def node2(bar, foo, baz):
        yield

    etl_graph = AsyncGraph(halt_on_exception=True)
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()

    assert etl_executor.data_flow_stats["node1"].get("in") == 0
    assert etl_executor.data_flow_stats["node1"].get("out") == 2
    assert etl_executor.data_flow_stats["node1"].get("err") == 0

    assert etl_executor.data_flow_stats["node2"].get("in") == 2
    assert etl_executor.data_flow_stats["node2"].get("out") == 0
    assert etl_executor.data_flow_stats["node2"].get("err") == 1


def test_yielding_a_tuple_to_unpack():
    async def node1():
        yield 1, 2
        yield 3, 4

    async def node2(foo, bar):
        assert foo in (1, 3)
        assert bar in (2, 4)
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()


def test_yielding_a_tuple_no_packing():
    async def node1():
        yield 1, 2
        yield 3, 4

    async def node2(foo, bar=None):
        assert foo in ((1, 2), (3, 4))
        assert bar is None
        yield

    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2, unpack_input=False)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()


def test_yielding_a_tuple_but_not_enough_values():
    async def node1():
        yield 1, 2
        yield 3, 4

    async def node2(foo, bar, baz):
        yield

    etl_graph = AsyncGraph(halt_on_exception=True)
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.execute()

    assert etl_executor.data_flow_stats["node1"].get("in") == 0
    assert etl_executor.data_flow_stats["node1"].get("out") == 2
    assert etl_executor.data_flow_stats["node1"].get("err") == 0

    assert etl_executor.data_flow_stats["node2"].get("in") == 2
    assert etl_executor.data_flow_stats["node2"].get("out") == 0
    assert etl_executor.data_flow_stats["node2"].get("err") == 1


def test_exceptions():
    async def node1():
        yield "hello"
        yield "world"

    async def node2(data):
        raise ValueError(f"bad data: {data}")
        yield

    graph = AsyncGraph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge("node1", "node2")

    executor = AsyncExecutor(graph)
    executor.execute()
    excs = executor.exceptions

    assert excs["node1"] == []
    assert len(excs["node2"]) == 2

    actual_exc_msgs = [e.args[0] for e in excs["node2"]]
    expected_exc_msgs = ["bad data: hello", "bad data: world"]
    assert actual_exc_msgs == expected_exc_msgs
    assert all(type(e) == ValueError for e in excs["node2"])

    assert executor.data_flow_stats["node1"].get("in") == 0
    assert executor.data_flow_stats["node1"].get("out") == 2
    assert executor.data_flow_stats["node1"].get("err") == 0

    assert executor.data_flow_stats["node2"].get("in") == 2
    assert executor.data_flow_stats["node2"].get("out") == 0
    assert executor.data_flow_stats["node2"].get("err") == 2
