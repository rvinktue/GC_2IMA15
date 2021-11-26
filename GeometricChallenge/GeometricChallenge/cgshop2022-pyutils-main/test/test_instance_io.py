from cgshop2022utils import io as cgsio
import os
import pytest
from tempfile import TemporaryDirectory


def test_read_website_example():
    path = os.path.join(os.path.dirname(__file__), 'verifiertests', "website_example.instance.json")
    instance = cgsio.read_instance(path)
    assert instance['id'] == 'tiny10'
    assert instance['type'] == 'Instance_CGSHOP2022'
    assert instance['meta'] == {'h': 1.0, 'l': 0.2, 'm': 10, 'n': 6}
    graph = instance['graph']
    assert len(graph.nodes) == 6
    assert len(graph.edges) == 10
    node_list = list(zip([60941, 66944, 42137, 42146, 63387, 55185], [77185, 32411, 48996, 64522, 19658, 34935]))
    assert list(graph.nodes) == node_list
    edge_index_list = list(zip([0, 0, 0, 0, 1, 2, 2, 3, 3, 4], [3, 2, 4, 1, 2, 4, 5, 4, 5, 5]))
    for ei, ej in edge_index_list:
        assert graph.has_edge(node_list[ei], node_list[ej])
    

def test_read_write_roundtrip():
    with TemporaryDirectory(suffix="_test_instance_io") as tmpdir:
        path = os.path.join(tmpdir, 'test.instance.json')
        graph = cgsio.random_instance()
        tmeta = {'metatest': [1,2,3]}
        cgsio.write_instance(path, graph, 'test_random_instance', tmeta)
        ri = cgsio.read_instance(path)
        assert ri['meta'] == tmeta
        rg = ri['graph']
        assert len(rg.nodes) == len(graph.nodes)
        assert len(rg.edges) == len(graph.edges)
        assert list(rg.nodes) == list(graph.nodes)
        for v1, v2 in graph.edges:
            assert rg.has_edge(v1, v2)

