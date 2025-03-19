import asyncio
import inspect
from collections import OrderedDict
from collections.abc import AsyncGenerator, Callable
from typing import Any, NamedTuple


class InvalidAsyncGraphError(Exception):
    pass


class _Node(NamedTuple):
    func: Callable[..., AsyncGenerator]
    name: str
    queue: asyncio.Queue | None
    queue_size: int
    max_tasks: int
    halt_on_exception: bool
    unpack_input: bool


class AsyncGraph:
    def __init__(self, halt_on_exception: bool = False) -> None:
        """Initialize a graph.

        Parameters
        ----------
        halt_on_exception : bool, optional
            To halt graph execution when *any* node has an unhandled exception,
            set this argument to ``True``. Defaults to ``False``.
        """
        self.halt_on_exception = halt_on_exception
        self._nodes: dict[str, _Node] = {}
        self._nodes_to_edges: OrderedDict[str, set[str]] = OrderedDict()

    def add_node(
        self,
        func: Callable[..., AsyncGenerator],
        *,
        name: str | None = None,
        halt_on_exception: bool = False,
        unpack_input: bool = True,
        max_tasks: int = 1,
        queue: asyncio.Queue | None = None,
        queue_size: int = 10_000,
        check_async_gen: bool = True,
    ) -> None:
        """Add a node by providing its function and optional configurations.

        Parameters
        ----------
        func : Callable[..., AsyncGenerator]
            The asynchronous generator function that this node runs.
            See notes below for the function's requirements.
        name : str, optional
            The name of this node. If not provided, the ``__name__`` attribute
            ``func`` is used.
        halt_on_exception : bool, optional
            To halt graph execution when this node has an unhandled exception,
            set this argument to ``True``. Defaults to ``False``.
        unpack_input : bool, optional
            By default (i.e., ``unpack_input`` is ``True``),
            ``func`` with arguments yielded from a source node is called as
            either ``func(*args)`` or ``func(**kwargs)``.
            To call ``func(arg)`` with no unpacking, set ``unpack_input`` to ``False``.
            See notes below for more details.
        max_tasks : int, optional
            The number of tasks that this node runs concurrently.
        queue : asyncio.Queue, optional
            The queue object that collects items from this node's source nodes,
            via ``await queue.put(item)``, and then feed into this node
            with items retrieved by ``await queue.get()``.
            This queue object must be an instance of either :class:`~asyncio.Queue` or
            a subclass of :class:`~asyncio.Queue`.
            If ``None`` or not given, it defaults to an ``asyncio.Queue()`` with max
            size set by ``queue_size``.
        queue_size : int, optional
            The maximum number of data items allowed to be
            in the queue object between this node as a destination node
            and its source node(s).

            .. deprecated:: 1.6.0
                The argument ``queue_size`` is deprecated and will be removed in
                v2.0.0. To configure the queue size, please use the argument ``queue``
                for a queue object whose queue size is set.
        check_async_gen : bool, optional
            If ``True`` (the default), the callable ``func`` is verified to be an async
            generator function by :func:`inspect.isasyncgenfunction`.
            Pass in ``False`` to disable this check if ``func`` would fail the check
            while the callable under the hood is still an async generator function
            (e.g., your function is wrapped by a decorator).

        Notes
        -----
        These details concern the requirements of the node's function and the keyword
        argument ``unpack_input``.

        * Each function in the graph must be an **asynchronous generator function**,
          i.e., it's defined by ``async def`` and it yields.

        * Each function can have any signature,
          with no arguments or with any valid argument types
          (`those listed here <https://docs.python.org/3/library/inspect.html#inspect.Parameter.kind>`_).
          This being said, because the functions are connected as a graph,
          in a given edge the destination function must be able to correctly handle
          whatever is yielded by the source function. Specifically:

          - If the destination function takes **no args**
            (i.e., ``async def dest_func():  # no input args``), then it is called
            as **dest_func()** with no args, regardless of what the source function yields.

          - If the destination function can take args,
            and if the source function yields a **tuple**,
            then the tuple ``args`` will be unpacked
            and **dest_func(*args)** will be called.

          - If the source function yields a **dict** instead,
            then **dest_func(**args)** will be called.

          - In case the destination function
            requires more input values than are available from the unpacked args
            (from either a tuple or dict), a ``TypeError`` is raised.

          - If the source function yields a tuple or dict,
            and for whatever reason you do *not* want to unpack it,
            set ``unpack_input`` to ``False`` at
            :meth:`~async_graph_data_flow.AsyncGraph.add_node`
            when constructing the :class:`~async_graph_data_flow.AsyncGraph` object.

          - If the destination function can take args,
            and if the source function yields an
            object that is **neither a tuple nor a dict**,
            then the destination function is simply called with the object ``obj``
            as **dest_func(obj)**.
            Note how you may take advantage of this behavior.
            For instance, when your destination function has keyword
            arguments
            (e.g., ``async def dest_func(a, b=..., c=...):  # b and c are kwargs``)
            calling ``dest_func(a)`` is valid with a value for ``a``
            yielded from the source function, and both ``b`` and ``c`` have their
            own default values.
        """  # noqa: E501

        name = name or func.__name__
        if check_async_gen and not inspect.isasyncgenfunction(func):
            raise TypeError(f"node '{name}' isn't an async generator function")
        if name in self._nodes:
            raise ValueError(f"node '{name}' already exists in the graph")
        if queue is not None and not isinstance(queue, asyncio.Queue):
            raise TypeError(f"queue must be an instance of asyncio.Queue: {queue}")
        self._nodes[name] = _Node(
            func=func,
            name=name,
            queue=queue,
            queue_size=queue_size,
            max_tasks=max_tasks,
            halt_on_exception=halt_on_exception,
            unpack_input=unpack_input,
        )
        self._nodes_to_edges[name] = set()

    def add_edge(
        self,
        src_node: str | Callable[..., AsyncGenerator],
        dst_node: str | Callable[..., AsyncGenerator],
    ) -> None:
        """Add an edge.

        Parameters
        ----------
        src_node : str | Callable[..., AsyncGenerator]
            The source node, either the function name or the function itself.
        dst_node : str | Callable[..., AsyncGenerator]
            The destination node, either the function name or the function itself.
        """
        if not isinstance(src_node, str):
            src_node = src_node.__name__
        if src_node not in self._nodes:
            raise ValueError(f"src_node '{src_node}' not registered in the graph")

        if not isinstance(dst_node, str):
            dst_node = dst_node.__name__
        if dst_node not in self._nodes:
            raise ValueError(f"dst_node '{dst_node}' not registered in the graph")

        self._nodes_to_edges[src_node].add(dst_node)

        if self._is_graph_cyclic():
            raise InvalidAsyncGraphError("Graph has a cycle")

    @property
    def nodes(self) -> list[dict[str, Any]]:
        """The list of nodes, each with its function and configurations."""
        return [node._asdict() for node in self._nodes.values()]

    @property
    def edges(self) -> set[tuple[str, str]]:
        """The set of edges, each with the names of the source and destination nodes."""
        return {
            (src_node, dst_node)
            for src_node, dst_nodes in self._nodes_to_edges.items()
            for dst_node in dst_nodes
        }

    @property
    def nodes_to_edges(self) -> dict[str, set[str]]:
        """The mapping between source nodes and their destination nodes."""
        return dict(self._nodes_to_edges)

    def _graph_validator(
        self,
        i: int,
        is_checked: list[bool],
        iter_stack: list[bool],
        graph: dict[str, set[str]],
    ) -> bool:
        """Code based on: https://www.geeksforgeeks.org/detect-cycle-in-a-graph/"""
        # Use the OrderedDict self._nodes_to_edges for its ordering.
        nodes = list(self._nodes_to_edges.keys())
        is_checked[i] = True
        iter_stack[i] = True

        try:
            dst_nodes = graph[nodes[i]]
        except KeyError:
            iter_stack[i] = False
            return False

        for dst_node in dst_nodes:
            try:
                edge_pos = nodes.index(dst_node)
            except ValueError:
                iter_stack[i] = False
                return False

            if not is_checked[edge_pos] and self._graph_validator(
                edge_pos, is_checked, iter_stack, graph
            ):
                return True
            elif iter_stack[edge_pos]:
                return True

        iter_stack[i] = False
        return False

    def _is_graph_cyclic(self) -> bool:
        """Code based on: https://www.geeksforgeeks.org/detect-cycle-in-a-graph/"""
        iter_stack = is_checked = [False] * (len(self._nodes) + 1)
        for i in range(len(self._nodes)):
            if not is_checked[i] and self._graph_validator(
                i, is_checked, iter_stack, self._nodes_to_edges
            ):
                return True
        return False

    def _get_start_nodes(self) -> set[str]:
        root_nodes = set()
        for src_node in self._nodes_to_edges.keys():
            root_node = True
            for dst_nodes in self._nodes_to_edges.values():
                if src_node in dst_nodes:
                    root_node = False
                    break

            if root_node:
                root_nodes.add(src_node)
        return root_nodes
