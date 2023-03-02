import asyncio
import inspect
import logging
import time
import traceback
from collections import deque
from typing import Any, Iterable, Optional

from .graph import AsyncGraph, InvalidAsyncGraphError


_LOG = logging.getLogger(__name__)

_DEFAULT_DATA_FLOW_LOGGING_NODE_FORMAT = " {node} - in={in}, out={out}, err={err}"
_DEFAULT_DATA_FLOW_LOGGING_TIME_INTERVAL = 60  # in seconds


class AsyncExecutor:
    def __init__(
        self,
        graph: AsyncGraph,
        *,
        logger: logging.Logger = None,
        max_exceptions: int = 1_000,
    ):
        """Initialize an executor.

        Parameters
        ----------
        graph : AsyncGraph
        logger : logging.Logger, optional
            Provide a logger for any customization.
            If not provided, a generic ``logging.getLogger(__name__)`` is used.
        max_exceptions : int, optional
            The maximum number of unhandled exceptions to keep track of at each node.
            If the number of exceptions at a node exceeds this threshold,
            only the most recent exceptions are kept.
            See also :attr:`~async_graph_data_flow.AsyncExecutor.exceptions`.
        """
        self._graph = graph
        if not isinstance(self._graph, AsyncGraph):
            raise TypeError(f"{self._graph} must be an AsyncGraph instance")

        self._node_queues = {}
        self._consumer_tasks = {}
        self._halt_pipeline_execution = False
        self._logger = logger if logger else _LOG
        self._max_exceptions = max_exceptions

        self._data_flow_stats = None
        self._data_flow_logging_lock = asyncio.Lock()
        self._data_flow_logging = False
        self._data_flow_logging_node_format = _DEFAULT_DATA_FLOW_LOGGING_NODE_FORMAT
        self._data_flow_logging_time_interval = _DEFAULT_DATA_FLOW_LOGGING_TIME_INTERVAL
        self._data_flow_logging_node_filter = self._graph._nodes.keys()
        self._data_flow_logging_last_timestamp = 0

        self._start_node_args = None

        self._exceptions = None

    @property
    def graph(self) -> AsyncGraph:
        """The graph to execute."""
        return self._graph

    @property
    def exceptions(self) -> dict[str, list[Exception]]:
        """Exceptions from the graph execution.

        The key is a node by name (str), and the value is the list of exceptions
        raised from the node.
        """
        from_deque_to_list = {}
        for node_name, excs in self._exceptions.items():
            # `excs` is a deque. Turning it into a list for user-friendliness.
            from_deque_to_list[node_name] = list(excs)
        return from_deque_to_list

    @property
    def data_flow_stats(self) -> dict[str, dict[str, int]]:
        """Data flow statistics.

        These statistics keep track of (i) the number of times data has passed
        into each node, (ii) the number of times data has come out of each node, and
        (iii) the number of errors each node has had.
        The key is a node by name (str), and the value is a dict with three keys (str)
        of ``"in"``, ``"out"``, and ``"err"``, each corresponding to its count (int)."""
        return self._data_flow_stats

    def turn_on_data_flow_logging(
        self,
        node_format: Optional[str] = None,
        node_filter: Iterable[str] = None,
        time_interval: Optional[int] = None,
        logger: logging.Logger = None,
    ):
        """Turn on and configure data flow logging.

        For a long-running graph execution,
        it is helpful to log such data flow information at a regular time interval.

        Parameters
        ----------
        node_format : str, optional
            Logging format for each node's statistics of (i) the number of times
            data has passed ``in`` the node, (ii) the number of times data has
            come ``out`` of the node, and (iii) the number of errors the node
            has had. If not provided, the default is
            ``" {node} - in={in}, out={out}, err={err}"``.
        node_filter: Iterable[str], optional
            Filter to see logs from only the specified nodes by name.
            If not provided, all nodes' statistics will be logged.
        time_interval: int, optional
            Time interval in seconds between data flow logs.
            If not provided, the default is 60 seconds.
        logger : logging.Logger, optional
            Provide a logger for any customization.
            If not provided, a generic ``logging.getLogger(__name__)`` is used.
        """
        self._data_flow_logging = True

        if node_format and isinstance(node_format, str):
            self._data_flow_logging_node_format = node_format

        if (
            node_filter
            and not isinstance(node_filter, str)
            and all(map(lambda x: isinstance(x, str), node_filter))
        ):
            self._data_flow_logging_node_filter = set(node_filter)

        if time_interval and isinstance(time_interval, int):
            self._data_flow_logging_time_interval = time_interval

        if logger and isinstance(logger, logging.Logger):
            self._logger = logger

    def turn_off_data_flow_logging(self):
        """Turn off data flow logging."""
        self._data_flow_logging = False

    async def _log_data_flow_nodes(self):
        for node, flow in self._data_flow_stats.items():
            if (
                self._data_flow_logging_node_filter
                and node not in self._data_flow_logging_node_filter
            ):
                continue

            self._logger.info(
                self._data_flow_logging_node_format.format(node=node, **flow)
            )

    async def _add_to_node_queue(self, edges: set[str], item: Any):
        for edge in edges:
            edge_queue = self._node_queues[edge]
            await edge_queue.put(item)

    async def _producer(self):
        """Push args to start nodes' queue in graph to begin pipeline."""
        for node, args in self._start_node_args.items():
            queue = self._node_queues[node]
            await queue.put(args)

    async def _consumer(self, node_name: str):
        """Consume and process data within the graph pipeline."""
        while True:
            try:
                if self._data_flow_logging and self._data_flow_logging_last_timestamp:
                    async with self._data_flow_logging_lock:
                        current_timestamp = time.time()
                        if (
                            current_timestamp - self._data_flow_logging_last_timestamp
                            > self._data_flow_logging_time_interval
                        ):
                            await self._log_data_flow_nodes()
                            self._data_flow_logging_last_timestamp = current_timestamp

                queue = self._node_queues[node_name]
                data = await queue.get()

                if self._halt_pipeline_execution:
                    queue.task_done()
                    continue

                node = self._graph._nodes[node_name]
                params = inspect.signature(node.func).parameters

                try:
                    if len(params) == 0:
                        coro = node.func()
                    elif node.unpack_input and (
                        (is_tuple := isinstance(data, tuple)) or isinstance(data, dict)
                    ):
                        coro = node.func(*data) if is_tuple else node.func(**data)
                    else:
                        coro = node.func(data)
                except asyncio.CancelledError:
                    continue
                except Exception as exc:
                    await self._update_data_flow_error_stats(node_name)
                    await self._update_exceptions(node_name, exc)
                    self._logger.error(traceback.format_exc())
                    if self._graph.halt_on_exception or node.halt_on_exception:
                        self._logger.error(
                            f"Pipeline execution halted due to an exception "
                            f"in {node_name} node"
                        )
                        self._halt_pipeline_execution = True
                        queue.task_done()
                    continue

                while True:
                    try:
                        # Stop data yielding/generation if _halt_pipeline_execution has
                        # been updated by other nodes
                        if self._halt_pipeline_execution:
                            raise StopAsyncIteration()

                        next_data_item = await anext(coro)
                        if isinstance(next_data_item, BaseException):
                            raise next_data_item
                    except StopAsyncIteration:
                        break
                    except asyncio.CancelledError:
                        break
                    except Exception as exc:
                        await self._update_data_flow_error_stats(node_name)
                        await self._update_exceptions(node_name, exc)
                        self._logger.error(traceback.format_exc())
                        if self._graph.halt_on_exception or node.halt_on_exception:
                            # close current agen
                            await coro.aclose()

                            self._logger.error(
                                f"Pipeline execution halted due to an exception "
                                f"in {node_name} node"
                            )
                            self._halt_pipeline_execution = True
                            break
                        else:
                            continue
                    else:
                        node_edges = self._graph._nodes_to_edges[node_name]
                        await self._update_data_flow_in_out_stats(node_name, node_edges)
                        await self._add_to_node_queue(node_edges, next_data_item)

                queue.task_done()
            except asyncio.CancelledError:
                break

    async def _update_data_flow_in_out_stats(self, in_node: str, out_nodes: set[str]):
        self._data_flow_stats[in_node]["out"] += 1
        for node in out_nodes:
            self._data_flow_stats[node]["in"] += 1

    async def _update_data_flow_error_stats(self, node: str):
        self._data_flow_stats[node]["err"] += 1

    async def _update_exceptions(self, node: str, exc: Exception):
        self._exceptions[node].append(exc)

    async def _pipeline_execution(self):
        self._data_flow_stats: dict[str, dict[str, int]] = {}
        self._exceptions: dict[str, deque[Exception]] = {}

        for node_name, node in self._graph._nodes.items():
            queue = asyncio.Queue(maxsize=node.queue_size)
            self._node_queues[node_name] = queue
            self._data_flow_stats[node_name] = {"in": 0, "out": 0, "err": 0}
            self._exceptions[node_name] = deque(maxlen=self._max_exceptions)

            for i in range(node.max_tasks):
                task_id = f"{node_name}_{i}"
                task = asyncio.create_task(self._consumer(node_name), name=task_id)
                self._consumer_tasks[task_id] = task

        await self._producer()

        for queue in self._node_queues.values():
            await queue.join()

        for task in self._consumer_tasks.values():
            task.cancel()

        await asyncio.gather(*self._consumer_tasks.values())

        if self._data_flow_logging:
            await self._log_data_flow_nodes()

    def _get_start_node_args(self, start_node_args) -> dict[str, tuple]:
        if start_node_args is None:
            start_node_args = {node: tuple() for node in self._graph._get_start_nodes()}
        if not start_node_args:
            raise InvalidAsyncGraphError("The graph has no start nodes")
        for node, args in start_node_args.items():
            if node not in self._graph._nodes:
                raise ValueError(f"The graph doesn't have the node '{node}'")
            if not isinstance(args, tuple):
                raise TypeError(f"args for the node '{node}' isn't a tuple: {args}")
        return start_node_args

    def execute(self, start_nodes: dict[str, tuple] = None) -> None:
        """Start executing the functions along the graph.

        Parameters
        ----------
        start_nodes : dict[str, tuple], optional
            Specify the start node(s), and optionally their arguments.
            Each key in this dictionary is the name (str) of the node function,
            and its corresponding value is the args (tuple)
            (in which case the node function will be called as ``func(*args)``
            -- provide ``None`` if you want ``func()`` with no args).
            If ``start_nodes`` is ``None`` or isn't provided,
            nodes that have no incoming edges are treated as start nodes.
        """
        self._start_node_args = self._get_start_node_args(start_nodes)
        self._data_flow_logging_last_timestamp = time.time()
        asyncio.run(self._pipeline_execution())
