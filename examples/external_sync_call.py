import asyncio
import time

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def extract():
    yield "hello"
    yield "world"


async def transform(data):
    print(f"Transformer received: {data}")
    await asyncio.sleep(3)
    yield str.title(data)


async def load1(data):
    print(f"Data in Load1: {data}")
    for i in range(0, 3):
        await asyncio.sleep(4)
        yield f"load1 {i}"


async def load2(data):
    print(f"Data in Load2: {data}")
    cloop = asyncio.get_running_loop()
    for i in range(0, 3):
        await cloop.run_in_executor(None, time.sleep, 4)
        yield f"load2 {i}"


async def output(data):
    print("output:", data)
    yield


if __name__ == "__main__":
    etl_graph = AsyncGraph()
    etl_graph.add_node(extract, name="extract", max_tasks=1, queue_size=1_000)
    etl_graph.add_node(transform)
    etl_graph.add_node(load1)
    etl_graph.add_node(load2)
    etl_graph.add_node(output)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load1")
    etl_graph.add_edge("transform", "load2")
    etl_graph.add_edge("load1", "output")
    etl_graph.add_edge("load2", "output")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    AsyncExecutor(etl_graph).execute()

    # Output:
    # -------
    # Graph: {
    #     'extract': {'transform'},
    #     'transform': {'load1', 'load2'},
    #     'load1': {'output'},
    #     'load2': {'output'},
    #     'output': set(),
    # }
    # Transformer received: hello
    # Transformer received: world
    # Data in Load1: Hello
    # Data in Load2: Hello
    # output: load1 0
    # output: load2 0
    # output: load1 1
    # output: load2 1
    # Data in Load1: World
    # output: load1 2
    # Data in Load2: World
    # output: load2 2
    # output: load1 0
    # output: load2 0
    # output: load1 1
    # output: load2 1
    # output: load1 2
    # output: load2 2
