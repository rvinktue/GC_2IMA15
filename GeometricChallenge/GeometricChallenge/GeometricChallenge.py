import matplotlib.pyplot as plt
import colorsys
import time
import networkx
from cgshop2022utils.io import read_instance, write_instance


# Colors in indices
def _debug_draw_graph(G, colors=None):
    if colors is None: colors = []
    if len(colors) != len(G.edges):
        colors = [0] * len(G.edges)
    maxim = float(max(colors) + 1)
    c = [colorsys.hsv_to_rgb(col / maxim, 1, 1) for col in colors]
    for i, (v, w) in enumerate(G.edges):
        plt.plot([v[0], w[0]], [v[1], w[1]], color=c[i])
    x = [node[0] for node in G.nodes]
    y = [node[1] for node in G.nodes]
    plt.scatter(x, y)


def _debug_draw_dual(nodes, edges):
    for (v, w) in edges:
        plt.plot([nodes[v][0], nodes[w][0]], [nodes[v][1], nodes[w][1]], color=(0, 0, 0))
    x = [node[0] for node in nodes]
    y = [node[1] for node in nodes]
    plt.scatter(x, y)
    for i, coord in enumerate(zip(x, y)):
        plt.annotate(str(i), coord)


def _intersect_segments(a, b, c, d):
    if a == c or a == d:
        return False

    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    x3 = c[0]
    y3 = c[1]
    x4 = d[0]
    y4 = d[1]
    D = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if D == 0:
        return False
    Px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / float(D)  # t*a[0] + (1-t)*b[0]
    Py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / float(D)  # t*a[1] + (1-t)*b[1]
    t1 = (Px - x1) / (x2 - x1)
    t2 = (Px - x3) / (x4 - x3)
    if 0 < t1 < 1 and 0 < t2 < 1:
        # plt.scatter(Px, Py, color = (1, 0, 0))
        # plt.scatter(x2, y2, color = (0, 0, 1))
        return True  # (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
    else:
        return False


def _naive_graph_generation(G):
    edges = []

    for i, e1 in enumerate(G.edges):
        for j, e2 in enumerate(G.edges):
            if j <= i:
                continue
            if _intersect_segments(e1[0], e1[1], e2[0], e2[1]):
                edges.append((i, j))

    return edges


t0 = time.time_ns()
instance_name = "sqrpecn73925"  # "reecn3382"
instance = read_instance("./instances/" + instance_name + ".instance.json")
print("Reading took: %s ms" % {(time.time_ns() - t0) / (10 ** 6)})

G = instance["graph"]
asj = [(list(G.nodes).index(u), list(G.nodes).index(v)) for (u, v) in G.edges]
t0 = time.time_ns()
intersections = _naive_graph_generation(G)
print("Naive graph generation took: %s ms" % ((time.time_ns() - t0) / (10 ** 6)))

markings = []
for (u, v) in intersections:
    markings.append(u)
    markings.append(v)

vertices = [[] for _ in range(len(G.edges))]
with open("edge_list_%s.txt" % {instance_name}, "w") as f:
    f.write("%s %s\n" % ({len(vertices)}, {len(intersections)}))
    for (i, j) in intersections:
        vertices[i].append(j)
        vertices[j].append(i)
        f.write("%s %s\n" % (i, j))

# print(vertices)
# colours = [0 if len(neighs) == 0 else -1 for neighs in vertices]
# for i in range(len(colours)):
#    if (len(vertices[i]) != 0):
#        colours[i] = max([colours[neigh] for neigh in vertices[i]]) + 1
#        #print("%s: gets color %s" % ({i}, {colours[i]}))

t0 = time.time_ns()
# _debug_draw_graph(G,colours)
# print(max(colours))
# plt.show()
print("Debug draw graph took: %s ms" % {(time.time_ns() - t0) / (10 ** 6)})
dual_nodes = [((ax + bx) / 2, (ay + by) / 2) for ((ax, ay), (bx, by)) in G.edges]

# write_solution("sol.json", instance_name, colours)
# _debug_draw_dual(dual_nodes,intersections)
