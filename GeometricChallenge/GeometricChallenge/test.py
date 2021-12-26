import matplotlib.pyplot as plt
import trapezoid as trapclass
import segment as segclass
import vertical_decomposition as vdclass
import geometry
import test_draw
import test_cases


# Handles test case (given list of vertex endpoints)
def handle_test(vertices, print_dag):
    segments = [segclass.Segment(vertices[2 * i], vertices[2 * i + 1]) for i in range(len(vertices) // 2)]
    vd = vdclass.VerticalDecomposition(geometry.find_bounding_box(vertices))

    for seg in segments:
        is_added = vd.add_segment(seg)
        if is_added:
            print("Added: (%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
            test_draw.test_draw_dag(vd.dag)
            plt.show()
        else:
            print("Could not add: (%s, %s) -> (%s, %s)"
                  % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))

    if print_dag:
        print(["%s, %s\n" % (node, vars(node)) for node in vd.dag.find_all(trapclass.Trapezoid)])


# Run all test cases (switch the False to True to print the final DAG for each test case)
for vertex_list in [
    test_cases.test_case_1(),
    test_cases.test_case_2(),
    test_cases.test_case_3(),
    test_cases.test_case_4()
]:
    handle_test(vertex_list, False)
