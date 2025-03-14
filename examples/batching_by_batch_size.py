import asyncio

from async_graph_data_flow import AsyncExecutor, AsyncGraph


class EndOfData:
    pass


class BatchQueue(asyncio.Queue):
    def __init__(self, batch_size: int | float):
        super().__init__()
        self.batch_size = batch_size
        self.batch: list = []

    async def put(self, item):
        # This custom queue class assumes the use of an EndOfData marker
        # to indicate the end of the data stream.
        if isinstance(item, EndOfData):
            if self.batch:
                await super().put(self.batch)
            # Don't forget to pass along the EndOfData marker.
            await super().put(item)
        else:
            self.batch.append(item)
            if len(self.batch) >= self.batch_size:
                await super().put(self.batch)
                self.batch = []


async def data_source():
    for i in range(1, 11):
        print(f"data_source yielding {i}")
        yield i
    # Indicate the end of the data stream,
    # so that the batch queue can flush the last batch.
    yield EndOfData()


async def batched_inputs(data):
    print(f"batched_inputs received: {data}")
    yield


if __name__ == "__main__":
    graph = AsyncGraph()

    graph.add_node(data_source)
    graph.add_node(batched_inputs, queue=BatchQueue(batch_size=4))

    graph.add_edge(data_source, batched_inputs)

    AsyncExecutor(graph).execute()

    # Output:
    # -------
    # data_source yielding 1
    # data_source yielding 2
    # data_source yielding 3
    # data_source yielding 4
    # data_source yielding 5
    # data_source yielding 6
    # data_source yielding 7
    # data_source yielding 8
    # data_source yielding 9
    # data_source yielding 10
    # batched_inputs received: [1, 2, 3, 4]
    # batched_inputs received: [5, 6, 7, 8]
    # batched_inputs received: [9, 10]
    # batched_inputs received: <__main__.EndOfData object at 0x10a990260>
