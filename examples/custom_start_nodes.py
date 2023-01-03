import logging

from async_graph_data_flow import AsyncExecutor, AsyncGraph


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


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_node(node3)
    etl_graph.add_edge("node1", "node2")
    etl_graph.add_edge("node2", "node3")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    etl_executor = AsyncExecutor(etl_graph)
    etl_executor.turn_on_data_flow_logging()
    etl_executor.execute(start_nodes={"node2": ("new_data",)})

    # Output:
    # -------
    # Graph: {'node1': {'node2'}, 'node2': {'node3'}, 'node3': set()}
    # Transformer received: new_data
    # Data in Load: data1
    # Data in Load: data2
    # INFO:async_graph_data_flow.executor: node1 - in=0, out=0, err=0
    # INFO:async_graph_data_flow.executor: node2 - in=0, out=2, err=0
    # INFO:async_graph_data_flow.executor: node3 - in=2, out=2, err=0
