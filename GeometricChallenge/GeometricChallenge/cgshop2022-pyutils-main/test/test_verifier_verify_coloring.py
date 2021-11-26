import cgshop2022utils.verify as cgv
from cgshop2022utils.io import random_instance, read_instance, read_solution
from random import random
import itertools
import os
from datetime import datetime
import networkx as nx
import json


def _check_color_class(edges):
    for e1, e2 in itertools.combinations(edges, 2):
        s1 = cgv.Segment(cgv.Point(e1[0][0], e1[0][1]), cgv.Point(e1[1][0], e1[1][1]))
        s2 = cgv.Segment(cgv.Point(e2[0][0], e2[0][1]), cgv.Point(e2[1][0], e2[1][1]))
        assert not cgv.do_intersect(s1, s2)

def _check_intersection(edges, si1, si2):
    e1 = edges[si1]
    e2 = edges[si2]
    s1 = cgv.Segment(cgv.Point(e1[0][0], e1[0][1]), cgv.Point(e1[1][0], e1[1][1]))
    s2 = cgv.Segment(cgv.Point(e2[0][0], e2[0][1]), cgv.Point(e2[1][0], e2[1][1]))
    assert cgv.do_intersect(s1, s2)

def test_verify_coloring_against_do_intersect():
    for i in range(5):
        ri = random_instance(n=75, p=0.5)
        index_to_edge = list(ri.edges)
        colors = [min(2, round(int(random()*3))) for _ in range(len(index_to_edge))]
        while True:
            error, num_colors = cgv.verify_coloring(index_to_edge, colors)
            if error is None:
                nc = 0
                for c in range(3):
                    cc = [e for i, e in enumerate(index_to_edge) if colors[i] == c]
                    if len(cc) > 0:
                        nc += 1
                    _check_color_class(cc)
                assert nc == num_colors
                break
            else:
                assert error.is_intersection
                inds = [error.segment_index1, error.segment_index2]
                assert colors[inds[0]] == colors[inds[1]]
                assert colors[inds[0]] == error.color_class
                _check_intersection(index_to_edge, inds[0], inds[1])
                remove_ind = 0 if random() < 0.5 else 1
                remove_ind = inds[remove_ind]
                index_to_edge.pop(remove_ind)
                colors.pop(remove_ind)

def test_verify_coloring_known_good():
    instance = read_instance(os.path.join(os.path.dirname(__file__), 'verifiertests', 'test113.instance.json'))
    assert instance['id'] == 'test113'
    graph = instance['graph']
    assert len(graph.nodes) == 35
    assert len(graph.edges) == 113
    inds = nx.get_edge_attributes(graph, 'idx')
    edges = list(graph.edges)
    edges.sort(key=(lambda e: inds[e]))
    assert edges[15] == ((35152, 10474), (7473, 62812))
    with open(os.path.join(os.path.dirname(__file__), 'verifiertests', 'test113.solution.json')) as solf:
        solution = json.load(solf)
    assert solution['num_colors'] == 11
    assert solution['instance'] == 'test113'
    t = datetime.now()
    res = cgv.verify_coloring(edges, solution['colors'])
    dt = (datetime.now() - t).total_seconds()
    assert res == (None, 11)
    assert dt < 0.5
    assert cgv.verify_coloring(graph, solution['colors']) == (None, 11)

def test_verify_coloring_known_bad():
    instance = read_instance(os.path.join(os.path.dirname(__file__), 'verifiertests', 'test113.instance.json'))
    assert instance['id'] == 'test113'
    graph = instance['graph']
    assert len(graph.nodes) == 35
    assert len(graph.edges) == 113
    with open(os.path.join(os.path.dirname(__file__), 'verifiertests', 'bad113.solution.json')) as solf:
        solution = json.load(solf)
    error, num_colors = cgv.verify_coloring(graph, solution['colors'])
    assert error is not None
    assert num_colors == 11

def test_verify_coloring_test_instance():
    instance = read_instance(os.path.join(os.path.dirname(__file__), 'verifiertests', 'test_verifier.instance.json'))
    assert instance['id'] == 'verifier_test'
    graph = instance['graph']
    expected_errors = {'collinear_test_verifier.solution.json': (True, ((-50,0),(0,0))),
                       'correct_test_verifier.solution.json': None,
                       'crossing_test_verifier.solution.json': (True, ((-5,-5),)),
                       'missing_test_verifier.solution.json': (False, None),
                       'wrongcount_test_verifier.solution.json': (False, None)}
    for file, errinfo in expected_errors.items():
        solution = read_solution(os.path.join(os.path.dirname(__file__), 'verifiertests', file))
        error, num_colors = cgv.verify_coloring(graph, solution['colors'], expected_num_colors=solution['num_colors'])
        if errinfo is None:
            assert error is None
            assert num_colors == 6
        else:
            assert error is not None
            if errinfo[0]:
                assert error.is_intersection
                assert error.approximate_x in {float(e[0]) for e in errinfo[1]}
                assert error.approximate_y in {float(e[1]) for e in errinfo[1]}
            else:
                assert not error.is_intersection

