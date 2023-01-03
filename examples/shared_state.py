import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


class SharedState:
    def __init__(self):
        self._dict = {}

    async def get(self, key):
        while True:
            try:
                return self._dict[key]
            except KeyError:
                await asyncio.sleep(0.001)

    async def set(self, key, value):
        self._dict[key] = value


async def node1(shared_state):
    await shared_state.set("current_data", "hello")
    yield shared_state
    await asyncio.sleep(2)

    await shared_state.set("current_data", "world")
    yield shared_state


async def node2(shared_state):
    current_data = await shared_state.get("current_data")
    print(f"node2 received: {current_data}")
    await asyncio.sleep(3)
    yield shared_state, current_data


if __name__ == "__main__":
    etl_graph = AsyncGraph()
    etl_graph.add_node(node1)
    etl_graph.add_node(node2)
    etl_graph.add_edge("node1", "node2")

    print(f"Graph: {etl_graph.nodes_to_edges}")
    shared_state = SharedState()
    AsyncExecutor(etl_graph).execute(start_nodes={"node1": (shared_state,)})

    # Output:
    # -------
    # Graph: {'node1': {'node2'}, 'node2': set()}
    # node2 received: hello
    # node2 received: world
