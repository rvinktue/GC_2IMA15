from cgshop2022utils.io import read_instance, write_instance  # Provided by the challenge
import random
import matplotlib.pyplot as plt


import trapezoid as trapclass
import segment as segclass
import vertex as vertclass
import vertical_decomposition as vdclass
import geometry



INPUT_FILE = "input_file_name"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file

# Incrementally build vertical decompositions of planar subgraphs
def main():
    # Read instance and instantiate graph, bounding box and starting vertical decomposition
    instance = read_instance(INPUT_FILE)  # read edges from input file
    g = instance["graph"]

    edges = g.edges
    random.shuffle(edges)  # Find random reordering of edges to decrease expected running time complexity

    bounding_box = geometry.find_bounding_box(g.nodes)
    vds = [vdclass.VerticalDecomposition(bounding_box)]

    # Init output file
    file = open(OUTPUT_FILE, 'w')
    file.write("%d %d \n" % (len(edges), len(g.nodes)))
    file.close()

    # Process all edges
    for edge in edges:
        for (key, vd) in vds:
            if vd.add_segment(edge):
                # If segment can be added to the vertical decomposition of level key: add it and continue to next edge
                continue
            elif key == len(vds):
                # If segment could not be added in any of the existing VDs, create a new VD
                new = vdclass.VerticalDecomposition(bounding_box)
                new.add_segment(edge)
                vds.append(new)

    # Return an upperbound on the edge-colouring
    return len(vds)


##### TESTING #####
def test_draw_DAG(root):
    trapezoids = get_all_content_of_type(root, trapclass.Trapezoid)
    segments = get_all_content_of_type(root, segclass.Segment)
    vertices = get_all_content_of_type(root, vertclass.Vertex)
    for t in trapezoids:
        assert isinstance(t, trapclass.Trapezoid), "t not a Trapezoid but a %s" % type(t).__name__
        test_draw_trapezoid(t)
    for s in segments:
        assert isinstance(s, segclass.Segment), "s not a Segment but a %s" % type(s).__name__
        test_draw_segment(s)
    for v in vertices:
        assert isinstance(v, vertclass.Vertex), "v not a Vertex but a %s" % type(v).__name__
        plt.scatter(v.x, v.y, color=(0,0,1))


def test_draw_segment(seg):
    plt.plot([seg.endpoint1.x, seg.endpoint2.x], [seg.endpoint1.y, seg.endpoint2.y], color=(0, 0, 0))


def get_all_content_of_type(root, content_type):
    contents = []
    stack = [root]
    while len(stack) > 0:
        node = stack.pop()
        if node is None:
            continue
        stack.append(node.left_child)
        stack.append(node.right_child)
        if isinstance(node.content, content_type):
            contents.append(node.content)
    return contents


def test_draw_trapezoid(trapezoid, color = (1, 0, 0)):
    a = trapezoid.top_segment.endpoint1
    b = trapezoid.top_segment.endpoint2
    c = trapezoid.bottom_segment.endpoint2
    d = trapezoid.bottom_segment.endpoint1
    lijstje = [a,b,c,d]
    lijstje.sort(key=lambda x: x.x)


    p = lijstje[1]
    q = lijstje[2]

    p_top = vertclass.Vertex(p.x, (a.y-b.y)/(a.x-b.x)*(p.x - a.x) + a.y)
    p_bot = vertclass.Vertex(p.x, (d.y-c.y)/(d.x-c.x)*(p.x - d.x) + d.y)

    q_top = vertclass.Vertex(q.x, (a.y - b.y) / (a.x - b.x)*(q.x - a.x) + a.y)
    q_bot = vertclass.Vertex(q.x, (d.y - c.y) / (d.x - c.x)*(q.x - d.x) + d.y)

    # top: y = (a.y-b.y)/(a.x-b.x)(x - a.x) + a.y
    # bot: y = (d.y-c.y)/(d.x-c.x)(x - d.x) + d.y

    xs, ys = zip(*[[p.x, p.y], [p_top.x, p_top.y]])
    plt.plot(xs, ys, color=color)
    xs, ys = zip(*[[p.x, p.y], [p_bot.x, p_bot.y]])
    plt.plot(xs, ys, color=color)
    xs, ys = zip(*[[q.x, q.y], [q_top.x, q_top.y]])
    plt.plot(xs, ys, color=color)
    xs, ys = zip(*[[q.x, q.y], [q_bot.x, q_bot.y]])
    plt.plot(xs, ys, color=color)


    xs, ys = zip(*[[q_top.x, q_top.y], [p_top.x, p_top.y]])
    plt.plot(xs, ys, color=color)
    xs, ys = zip(*[[q_bot.x, q_bot.y], [p_bot.x, p_bot.y]])
    plt.plot(xs, ys, color=color)


def test_draw_graph(vertices, segments):
    for seg in segments:
        print("(%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
        plt.plot([seg.endpoint1.x, seg.endpoint2.x], [seg.endpoint1.y, seg.endpoint2.y], color=(0,0,0))
    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    plt.scatter(x, y)
    test_draw_trapezoid(geometry.find_bounding_box(vertices))


vertices = [vertclass.Vertex(1, 1), vertclass.Vertex(10, 1),
            vertclass.Vertex(11, 1), vertclass.Vertex(12, 1),
            ]
vd = vdclass.VerticalDecomposition(geometry.find_bounding_box(vertices))

segments = [
            segclass.Segment(vertices[0], vertices[1]),
            segclass.Segment(vertices[2], vertices[3]),
           ]

#test_draw_graph(vertices,segments)
#plt.show()

vd.add_segment(segments[0])
node = vd.find_point_location(vertclass.Vertex(5, 2))
for n in node.right_neighbours:
    test_draw_trapezoid(n.content)
test_draw_trapezoid(node.content, (0, 0, 1))
plt.show()
test_draw_DAG(vd.dag)
plt.show()


for seg in segments:
    print("Before adding: ")
    trap1 = vd.find_point_location(seg.endpoint1).content
    trap2 = vd.find_point_location(seg.endpoint2).content
    print("First trapezoid: %s" % trap1)
    print("Second trapezoid: %s" % trap2)
    test_draw_trapezoid(trap1)
    # plt.show()
    test_draw_trapezoid(trap2)
    # plt.show()
    is_added = vd.add_segment(seg)
    if is_added:
        print("Added: (%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
        test_draw_DAG(vd.dag)
        plt.show()
    else:
        print("Could not add: (%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
