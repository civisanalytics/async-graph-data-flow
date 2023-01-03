import asyncio
import logging

from async_graph_data_flow import AsyncExecutor, AsyncGraph


async def extract():
    for i in range(0, 3):
        await asyncio.sleep(3)
        yield "hello"


async def transform(data):
    print(f"Transformer received: {data}")
    # await asyncio.sleep(3)
    yield str.title(data)


async def load(data):
    print(f"Data in Load: {data}")
    yield


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    etl_graph = AsyncGraph()
    etl_graph.add_node(extract, name="extract", max_tasks=1, queue_size=1_000)
    etl_graph.add_node(transform)
    etl_graph.add_node(load)
    etl_graph.add_edge("extract", "transform")
    etl_graph.add_edge("transform", "load")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    etl_executor = AsyncExecutor(etl_graph)

    etl_executor.turn_on_data_flow_logging(
        time_interval=3, node_filter=["transform", "load"]
    )
    etl_executor.execute()

    # Output:
    # -------
    # Graph: {'extract': {'transform'}, 'transform': {'load'}, 'load': set()}
    # Transformer received: hello
    # Data in Load: Hello
    # INFO:async_graph_data_flow.executor: transform - in=1, out=1, err=0
    # INFO:async_graph_data_flow.executor: load - in=1, out=0, err=0
    # INFO:async_graph_data_flow.executor: transform - in=2, out=2, err=0
    # INFO:async_graph_data_flow.executor: load - in=2, out=1, err=0
    # Transformer received: hello
    # Data in Load: Hello
    # Transformer received: hello
    # Data in Load: Hello
    # INFO:async_graph_data_flow.executor: transform - in=3, out=2, err=0
    # INFO:async_graph_data_flow.executor: load - in=2, out=2, err=0
    # INFO:async_graph_data_flow.executor: transform - in=3, out=3, err=0
    # INFO:async_graph_data_flow.executor: load - in=3, out=3, err=0
