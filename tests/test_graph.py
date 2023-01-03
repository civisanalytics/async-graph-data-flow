from unittest import mock

import pytest

from async_graph_data_flow.graph import InvalidAsyncGraphError
from async_graph_data_flow import AsyncGraph


def async_graph_with_nodes_mock():
    async def extract_node(message):
        yield "hello"

    async def transform_node(message):
        yield "hello"

    async def load_node(message):
        yield "hello"

    etl_graph = AsyncGraph()
    etl_graph.add_node(extract_node)
    etl_graph.add_node(transform_node)
    etl_graph.add_node(load_node)
    return etl_graph


def async_graph_without_nodes_mock():
    etl_graph = AsyncGraph()
    return etl_graph


class TestAsyncGraphAddNode:
    def test_add_node_with_invalid_node_args(self):
        etl_graph = async_graph_without_nodes_mock()
        assert len(etl_graph._nodes.keys()) == 0

        with pytest.raises(TypeError) as excinfo:
            etl_graph.add_node(None, name="none_node")
        assert str(excinfo.value) == (
            "node 'none_node' isn't an async generator function"
        )

    def test_add_node_with_valid_node_args(self):
        etl_graph = async_graph_without_nodes_mock()
        assert len(etl_graph._nodes.keys()) == 0

        async def extract_node(message):
            yield "hello"

        etl_graph.add_node(extract_node)
        assert len(etl_graph._nodes.keys()) == 1
        assert etl_graph._nodes["extract_node"].name == "extract_node"
        assert etl_graph._nodes["extract_node"].func == extract_node

    def test_nodes(self):
        graph = async_graph_with_nodes_mock()
        assert graph.nodes == [
            {
                "func": mock.ANY,
                "halt_on_exception": False,
                "max_tasks": 1,
                "name": "extract_node",
                "queue_size": 10_000,
                "unpack_input": True,
            },
            {
                "func": mock.ANY,
                "halt_on_exception": False,
                "max_tasks": 1,
                "name": "transform_node",
                "queue_size": 10_000,
                "unpack_input": True,
            },
            {
                "func": mock.ANY,
                "halt_on_exception": False,
                "max_tasks": 1,
                "name": "load_node",
                "queue_size": 10_000,
                "unpack_input": True,
            },
        ]


class TestAsyncGraphAddEdge:
    def test_add_edge_with_invalid_src_edge_args(self):
        etl_graph = async_graph_with_nodes_mock()
        assert len(etl_graph.edges) == 0

        with pytest.raises(ValueError) as excinfo:
            etl_graph.add_edge(src_node="invalid_src_node", dst_node="transform_node")
        assert str(excinfo.value) == (
            "src_node 'invalid_src_node' not registered in the graph"
        )

    def test_add_edge_with_invalid_dst_edge_args(self):
        etl_graph = async_graph_with_nodes_mock()
        assert len(etl_graph.edges) == 0

        with pytest.raises(ValueError) as excinfo:
            _ = etl_graph.add_edge(src_node="extract_node", dst_node="invalid_dst_node")
        assert str(excinfo.value) == (
            "dst_node 'invalid_dst_node' not registered in the graph"
        )

    def test_add_edge_with_valid_edge_args(self):
        etl_graph = async_graph_with_nodes_mock()
        assert len(etl_graph.edges) == 0

        etl_graph.add_edge(src_node="extract_node", dst_node="transform_node")
        assert len(etl_graph.edges) == 1
        assert etl_graph.edges == {("extract_node", "transform_node")}

    def test_add_edge_graph_acyclic(self):
        etl_graph = async_graph_with_nodes_mock()

        with pytest.raises(InvalidAsyncGraphError) as excinfo:
            etl_graph.add_edge(src_node="extract_node", dst_node="transform_node")
            etl_graph.add_edge(src_node="transform_node", dst_node="load_node")
            etl_graph.add_edge(src_node="load_node", dst_node="extract_node")

        assert "Graph has a cycle" in str(excinfo.value)
