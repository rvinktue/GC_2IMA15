import sys
import json
import networkx as nx
from networkx.utils import open_file
import matplotlib.pyplot as plt
from cgshop2022utils import io as cgsio


@open_file(0, mode="w")
def write_solution(
    path,
    g: nx.Graph,
    colordict,
    ncol: int = None,
    limit: int = 0,
):
    # transform the formless dict from uptop into an tuple->int attribute mapping
    col = {edges[key]: value for key, value in colordict.items()}
    nx.set_edge_attributes(g, col, "color")

    # regain information as idx->color dict
    idxcol = {d[2]["idx"]: d[2]["color"] for d in g.edges(data=True)}
    # get the idx->color mapping sorted and only the color of it
    colors = [value for key, value in sorted(idxcol.items(), key=lambda item: item[0])]
    if ncol is None:
        ncol = len(set(colors))

    json.dump(
        obj={
            "type": "Solution_CGSHOP2022",
            "instance": "verifier_test",
            "num_colors": ncol,
            "colors": colors[0 : len(colors) - limit],
        },
        fp=path,
    )



nodes = {
    "origin": (0, 0),
    "faraway1": (2**31 + 2, 2**31 + 1),
    "faraway2": (2**31 + 1, 2**31 + 2),
    "square1": (0, -10),
    "square2": (-10, -10),
    "square3": (-10, 0),
    "collin1": (-100, 0),
    "collin2": (-50, 0),
    "fp32-fakecollin1": (1, 33554432 + 1),
    "fp32-fakecollin2": (2, 67108864),
}
edges = {
    "of1": (nodes["origin"], nodes["faraway1"]),
    "of2": (nodes["origin"], nodes["faraway2"]),
    "of3": (nodes["faraway1"], nodes["faraway2"]),
    "s1": (nodes["origin"], nodes["square1"]),
    "s2": (nodes["square1"], nodes["square2"]),
    "s3": (nodes["square2"], nodes["square3"]),
    "s4": (nodes["square3"], nodes["origin"]),
    "d1": (nodes["square2"], nodes["origin"]),
    "d2": (nodes["square3"], nodes["square1"]),
    "c1": (nodes["origin"], nodes["collin1"]),
    "c2": (nodes["origin"], nodes["collin2"]),
    "fc1": (nodes["origin"], nodes["fp32-fakecollin1"]),
    "fc2": (nodes["fp32-fakecollin2"], nodes["origin"]),
    "fc3": (nodes["fp32-fakecollin1"], nodes["fp32-fakecollin2"]),
}
g = nx.Graph()
g.add_edges_from(edges.values())

# write and reread to get idx data and ensure the right instance is in place
cgsio.write.write_instance(
    path="test_verifier.instance.json", g=g, id="verifier_test", meta={}
)
g = None
g = cgsio.read.read_instance(path="test_verifier.instance.json")["graph"]

colors_correct = {
    # none of the far-away objects are overlapping
    "of1": 0, 
    "of2": 0,
    "of3": 0,
    # none (except the diagonals) in the square are overlapping
    "s1": 1,
    "s2": 1,
    "s3": 1,
    "s4": 1,
    "d1": 1,
    "d2": 2,
    # collinears are not allowed
    "c1": 3,
    "c2": 4,
    # none of these are overlapping, but fp32 might indicate so 
    "fc1": 5,
    "fc2": 5,
    "fc3": 5,
}

write_solution(
    path="correct_test_verifier.solution.json", g=g, colordict=colors_correct
)
write_solution(
    path="wrongcount_test_verifier.solution.json", g=g, colordict=colors_correct, ncol=5
)
write_solution(
    path="missing_test_verifier.solution.json", g=g, colordict=colors_correct, limit=1
)
col = colors_correct.copy()
col["d2"] = 1
write_solution(path="crossing_test_verifier.solution.json", g=g, colordict=col)
col = colors_correct.copy()
col["c2"] = 3
write_solution(path="collinear_test_verifier.solution.json", g=g, colordict=col)
