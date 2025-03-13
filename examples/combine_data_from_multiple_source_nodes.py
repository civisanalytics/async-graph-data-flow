import asyncio
import itertools

from async_graph_data_flow import AsyncExecutor, AsyncGraph


class CombineDataQueue(asyncio.Queue):
    def __init__(self, node_order: list[str]):
        super().__init__()
        self.node_order = node_order
        self.queues = {node: asyncio.Queue() for node in node_order}

    async def put(self, item):
        node, *data = item
        if node not in self.node_order:
            raise ValueError(f"Node {node} not in node order {self.node_order}")
        if not data:
            raise ValueError(f"Data missing for node {node}")
        await self.queues[node].put(data)
        if all(not q.empty() for q in self.queues.values()):
            new = tuple(
                itertools.chain(*((q.get_nowait()) for q in self.queues.values()))
            )
            await super().put(new)


async def threes():
    for _ in range(3):
        print("threes yielding 3")
        yield "threes", 3


async def fours():
    for _ in range(4):
        print("fours yielding 4")
        yield "fours", 4


async def fives():
    for _ in range(5):
        print("fives yielding 5")
        yield "fives", 5


async def final_node(int1, int2, int3):
    print(f"Final node received {int1}, {int2}, {int3}")
    yield


if __name__ == "__main__":
    graph = AsyncGraph()

    graph.add_node(threes)
    graph.add_node(fours)
    graph.add_node(fives)
    graph.add_node(final_node, queue=CombineDataQueue(["threes", "fours", "fives"]))

    graph.add_edge("threes", "final_node")
    graph.add_edge("fours", "final_node")
    graph.add_edge("fives", "final_node")

    AsyncExecutor(graph).execute()

    # Output:
    # -------
    # threes yielding 3
    # threes yielding 3
    # threes yielding 3
    # fours yielding 4
    # fours yielding 4
    # fours yielding 4
    # fours yielding 4
    # fives yielding 5
    # fives yielding 5
    # fives yielding 5
    # fives yielding 5
    # fives yielding 5
    # Final node received 3, 4, 5
    # Final node received 3, 4, 5
    # Final node received 3, 4, 5
