import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def extract():
    yield "hello"
    await asyncio.sleep(5)
    yield "world"


async def transform(data):
    print(f"Transforming data: {data}")
    new_msg = str.title(data)
    await asyncio.sleep(3)
    yield new_msg


async def load(data):
    await asyncio.sleep(5)
    print(f"Loading data {data}")
    yield


async def print_data(data):
    print(f"Printing data: {data}")
    yield


async def end_task():
    print("Ending Tasks")
    yield


if __name__ == "__main__":
    etl_graph = AsyncGraph()
    etl_graph.add_node(extract, name="extract", max_tasks=1, queue_size=1_000)
    etl_graph.add_node(transform, max_tasks=2)
    etl_graph.add_node(load, max_tasks=2)
    etl_graph.add_node(print_data, max_tasks=2)
    etl_graph.add_node(end_task, max_tasks=2)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")
    etl_graph.add_edge("transform", "print_data")
    etl_graph.add_edge("load", "end_task")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    AsyncExecutor(etl_graph).execute()

    # Output:
    # -------
    # Graph: {
    #     'extract': {'transform'},
    #     'transform': {'print_data', 'load'},
    #     'load': {'end_task'},
    #     'print_data': set(),
    #     'end_task': set(),
    # }
    # Transforming data: hello
    # Printing data: Hello
    # Transforming data: world
    # Loading data Hello
    # Printing data: World
    # Ending Tasks
    # Loading data World
    # Ending Tasks
