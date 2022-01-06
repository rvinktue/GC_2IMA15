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
    vd = vdclass.VerticalDecomposition(geometry.find_bounding_box([[v.x, v.y] for v in vertices]))

    for seg in segments:
        start_node, end_node = vd.point_location_segment(seg)
        is_added = vd.add_segment(seg)
        # if is_added:
        #     print("Added: (%s, %s) -> (%s, %s)" % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
        #     # test_draw.test_draw_dag(vd.dag)
        #     # for trap in vd.dag.find_all(trapclass.Trapezoid):
        #     #     test_draw.test_draw_trapezoid(trap.content, (190/255, 190/255, 190/255))
        #     #     plt.show()
        #     #     test_draw.test_draw_dag(vd.dag)
        #     # plt.show()
        # else:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True, sharey=True)
        test_draw.test_draw_dag(vd.dag, ax=ax1)
        # print("Could not add: (%s, %s) -> (%s, %s)"
        #       % (seg.endpoint1.x, seg.endpoint1.y, seg.endpoint2.x, seg.endpoint2.y))
        for neighbour in start_node.right_neighbours:
            test_draw.test_draw_trapezoid(neighbour.content, ax=ax2)
        test_draw.test_draw_dag(vd.dag, ax=ax1)
        test_draw.test_draw_trapezoid(start_node.content, ax=ax3)
        test_draw.test_draw_trapezoid(end_node.content, ax=ax4)
        plt.show()

    if print_dag:
        print(["%s, %s\n" % (node, vars(node)) for node in vd.dag.find_all(trapclass.Trapezoid)])


# Run all test cases (switch the False to True to print the final DAG for each test case)
for index, vertex_list in enumerate([
    # test_cases.test_case_1(),
    # test_cases.test_case_2(),
    # test_cases.test_case_3(),
    # test_cases.test_case_4(),
    test_cases.test_case_5()
]):
    print(f"Running test {index}")
    handle_test(vertex_list, False)
