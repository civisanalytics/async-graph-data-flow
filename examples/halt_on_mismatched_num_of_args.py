import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def extract():
    for i in range(4):
        yield i


async def transform(data):
    print(f"Transformer received: {data}")

    if data == 2:
        yield 0, 1

    await asyncio.sleep(3)
    yield data


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
    # Transformer received: 0
    # Transformer received: 1
    # Data in Load: 0
    # Transformer received: 2
    # Data in Load: 1
    # Traceback (most recent call last):
    #   File "/path/to/src/async_graph_data_flow/executor.py", line 164, in _consumer
    #     coro = node.func(*data) if is_tuple else node.func(**data)
    # TypeError: load() takes 1 positional argument but 2 were given
    #
    # Transformer received: 3
    # Data in Load: 2
    # Data in Load: 3
