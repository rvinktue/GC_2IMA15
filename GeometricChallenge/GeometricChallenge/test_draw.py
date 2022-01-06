import matplotlib.pyplot as plt
import trapezoid as trapclass
import segment as segclass
import vertex as vertclass
import geometry


def test_draw_dag(root):
    trapezoids = get_all_content_of_type(root, trapclass.Trapezoid)
    segments = get_all_content_of_type(root, segclass.Segment)
    vertices = get_all_content_of_type(root, vertclass.Vertex)
    for t in trapezoids:
        test_draw_trapezoid(t)
    for s in segments:
        test_draw_segment(s)
    for v in vertices:
        plt.scatter(v.x, v.y, color=(0, 0, 1))


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


def test_draw_trapezoid(trapezoid, color=(1, 0, 0)):
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
        plt.plot([seg.endpoint1.x, seg.endpoint2.x], [seg.endpoint1.y, seg.endpoint2.y], color=(0, 0, 0))
    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    plt.scatter(x, y)
    test_draw_trapezoid(geometry.find_bounding_box(vertices))
