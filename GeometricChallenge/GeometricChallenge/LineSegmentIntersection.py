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


def test_draw_segment(seg, color=(0, 0, 0)):
    plt.plot([seg.endpoint1.x, seg.endpoint2.x], [seg.endpoint1.y, seg.endpoint2.y], color=color)


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
    p_top = trapezoid.left_segment.endpoint2
    p_bot = trapezoid.left_segment.endpoint1

    q_top = trapezoid.right_segment.endpoint2
    q_bot = trapezoid.right_segment.endpoint1

    test_draw_segment(trapezoid.left_segment, color)
    test_draw_segment(trapezoid.right_segment, color)
    test_draw_segment(segclass.Segment(p_top, q_top), color)
    test_draw_segment(segclass.Segment(p_bot, q_bot), color)


def test_draw_graph(vertices, segments):
    for seg in segments:
        print("(%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
        plt.plot([seg.endpoint1.x, seg.endpoint2.x], [seg.endpoint1.y, seg.endpoint2.y], color=(0,0,0))
    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    plt.scatter(x, y)
    test_draw_trapezoid(geometry.find_bounding_box(vertices))


vertices = [vertclass.Vertex(1, 1), vertclass.Vertex(10, 1),
            vertclass.Vertex(1, 2), vertclass.Vertex(3, 2),
            vertclass.Vertex(5, 2), vertclass.Vertex(7, 2),
            vertclass.Vertex(9, 2), vertclass.Vertex(11, 2),
            vertclass.Vertex(0, 3), vertclass.Vertex(2, 3),
            ]

segments = [ segclass.Segment(vertices[2*i], vertices[2*i+1]) for i in range(len(vertices)//2) ]


vd = vdclass.VerticalDecomposition(geometry.find_bounding_box(vertices))

for seg in segments:
    trap_node1 = vd.find_point_location(seg.endpoint1)
    trap_node2 = vd.find_point_location(seg.endpoint2)
    trap1 = trap_node1.content
    trap2 = trap_node2.content
    is_added = vd.add_segment(seg)
    if is_added:
        print("Added: (%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
        test_draw_DAG(vd.dag)
        plt.show()
    else:
        print("Could not add: (%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
