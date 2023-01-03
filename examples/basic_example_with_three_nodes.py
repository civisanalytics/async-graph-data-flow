import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def extract():
    yield "hello"
    yield "world"


async def transform(data):
    print(f"Transformer received: {data}")
    await asyncio.sleep(3)
    yield str.title(data)


async def load(data):
    print(f"Data in Load: {data}")
    yield


if __name__ == "__main__":
    etl_graph = AsyncGraph()
    etl_graph.add_node(extract, name="extract", max_tasks=1, queue_size=1_000)
    etl_graph.add_node(transform)
    etl_graph.add_node(load)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    AsyncExecutor(etl_graph).execute()

    # Output:
    # -------
    # Graph: {'extract': {'transform'}, 'transform': {'load'}, 'load': set()}
    # Transformer received: hello
    # Transformer received: world
    # Data in Load: Hello
    # Data in Load: World
