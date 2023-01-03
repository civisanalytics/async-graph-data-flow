import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def extract():
    yield "hello"
    yield "world"
    yield "civis"
    yield "analytics"
    yield "done"


async def transform(data):
    # print(f"Transformer: {data}")
    await asyncio.sleep(3)
    yield str.title(data)


async def load(data):
    print(f"Load: {data}")

    if data in ["World", "Analytics"]:
        await asyncio.sleep(0)
        raise Exception(f"intentional error for {data}")

    yield data


async def output(data):
    print("output:", data)
    yield


if __name__ == "__main__":
    etl_graph = AsyncGraph(halt_on_exception=True)
    etl_graph.add_node(extract, name="extract", max_tasks=1, queue_size=1_000)
    etl_graph.add_node(transform)
    etl_graph.add_node(load)
    etl_graph.add_node(output)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")
    etl_graph.add_edge("load", "output")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    AsyncExecutor(etl_graph).execute()

    # Output:
    # -------
    # Graph: {
    #     'extract': {'transform'},
    #     'transform': {'load'},
    #     'load': {'output'},
    #     'output': set(),
    # }
    # Load: Hello
    # output: Hello
    # Load: World
    # Traceback (most recent call last):
    #   File "/path/to/src/async_graph_data_flow/executor.py", line 188, in _consumer
    #     next_data_item = await anext(coro)
    #   File "/path/to/examples/halt_on_exception_at_any_node.py", line 25, in load
    #     raise Exception(f"intentional error for {data}")
    # Exception: intentional error for World
    #
    # Pipeline execution halted due to an exception in load node
