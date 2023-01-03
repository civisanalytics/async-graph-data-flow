import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


BUFFER = 3
count = 0
batch_list = []


async def extract():
    i = 1
    while i <= 10:
        yield i**2
        i += 1
        await asyncio.sleep(1)
    yield


async def transform(data):
    print(f"Transformer received: {data}")
    await asyncio.sleep(3)
    if not data:
        yield data
    else:
        yield data**3


async def load(data):
    global count, batch_list

    if data:
        print("Batching data in memory")
        batch_list.append(data)
        count += 1

    if count >= BUFFER:
        print("Flushing data:", batch_list)
        count = 0
        batch_list = []

    if not data and batch_list:
        print("Flushing remaining data:", batch_list)
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
    # Transformer received: 1
    # Transformer received: 4
    # Batching data in memory
    # Transformer received: 9
    # Batching data in memory
    # Transformer received: 16
    # Batching data in memory
    # Flushing data: [1, 64, 729]
    # Transformer received: 25
    # Batching data in memory
    # Transformer received: 36
    # Batching data in memory
    # Transformer received: 49
    # Batching data in memory
    # Flushing data: [4096, 15625, 46656]
    # Transformer received: 64
    # Batching data in memory
    # Transformer received: 81
    # Batching data in memory
    # Transformer received: 100
    # Batching data in memory
    # Flushing data: [117649, 262144, 531441]
    # Transformer received: None
    # Batching data in memory
    # Flushing remaining data: [1000000]
