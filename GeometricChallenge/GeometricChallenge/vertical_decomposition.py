import dagnode as dag
import trapezoid as trapclass
import test_draw
import matplotlib.pyplot as plt

# Class that represents the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        self.dag = dag.DagNode(bounding_box)

    # Finds and returns the trapezoid in which the requested point lies in associated DAG node
    def find_point_location(self, point):
        current_node = self.dag.choose_next(point)
        while not isinstance(current_node.content, trapclass.Trapezoid):
            current_node = current_node.choose_next(point)
        assert isinstance(current_node.content, trapclass.Trapezoid), \
            "Expected to find type(current_node.content) = Trapezoid, instead found %s" \
            % type(current_node.content).__name__
        return current_node  # Return DAG node containing trapezoid

    def point_location_segment(self, segment):
        current_node_1 = self.dag
        while not isinstance(current_node_1.content, trapclass.Trapezoid):
            current_node_1 = current_node_1.choose_next_segmented(segment, segment.endpoint1)
        trap_point_1 = current_node_1

        current_node_2 = self.dag
        while not isinstance(current_node_2.content, trapclass.Trapezoid):
            current_node_2 = current_node_2.choose_next_segmented(segment, segment.endpoint2)
        trap_point_2 = current_node_2
        # returns point location of left endpoint, point location of right endpoint
        return trap_point_1, trap_point_2


    # Finds all trapezoids intersected by segment (assuming segment does not intersect any existing edges in the VD)
    def find_intersecting_trapezoids(self, segment):
        # start_node = self.find_point_location(segment.endpoint1)
        # end_node = self.find_point_location(segment.endpoint2)
        start_node, end_node = self.point_location_segment(segment)
        intersected_trapezoids = [start_node]
        current_node = start_node

        while current_node is not end_node:
            if __debug__:
                if current_node.right_neighbours == []:
                    test_draw.test_draw_dag(self.dag)
                    test_draw.test_draw_segment(segment)
                    plt.show()
                    print("oh")
            assert current_node.right_neighbours != [], "Current node has no neighbours, but is not end node"
            # Go to the next trapezoid on the path
            # assert len([n for n in current_node.right_neighbours if n.content.segment_enter(segment)]) > 0, "will get stuck"
            temp = [n for n in current_node.right_neighbours if n.content.segment_enter(segment)]
            if __debug__:
                if (len(temp) == 0):
                    test_draw.test_draw_dag(self.dag)
                    test_draw.test_draw_segment(segment)
                    plt.show()
                    assert False, "oh"
            for node in current_node.right_neighbours:
                trap = node.content
                assert isinstance(trap, trapclass.Trapezoid), \
                    "expected type(trap) = Trapezoid, found %s" % type(trap).__name__
                if trap.segment_enter(segment):
                    # Found the successor
                    intersected_trapezoids.append(node)
                    current_node = node
                    break
        if __debug__:
            print("Segment forms path through %s trapezoids" % len(intersected_trapezoids))
        return intersected_trapezoids

    # Adds a new segment to the vertical decomposition if it does not intersect
    # Returns True if segment could be inserted in this vertical decomposition
    #         False if segment could not be inserted in this vertical decomposition
    def add_segment(self, segment):
        # Naively check all trapezoids for intersections @TODO: we can probably improve this
        all_trapezoids = self.dag.find_all(trapclass.Trapezoid)

        intersection_found = False
        for node in all_trapezoids:
            trapezoid = node.content
            assert isinstance(trapezoid, trapclass.Trapezoid), \
                "Expected type(trapezoid) = Trapezoid, instead found %s" % type(trapezoid).__name__
            # Checks if the segment has an intersection with the bottom segment of the trapezoid
            if trapezoid.is_violated_by_segment(segment):
                # @TODO: write intersection to file for C++
                intersection_found = True

        if intersection_found:
            return False

        # Add segment to DAG
        self.update(self.find_intersecting_trapezoids(segment), segment)
        return True

    # Updates the DAG with the new trapezoids induced by adding segment
    def update(self, nodes, segment):
        if len(nodes) == 1 and nodes[0].content.left_points[0].x_order(segment.endpoint1) != 0 and nodes[0].content.right_points[0].x_order(segment.endpoint2) != 0:
            # Segment is completely contained in a single trapezoid
            node = nodes[0]
            trapezoid = node.content

            assert isinstance(trapezoid, trapclass.Trapezoid), \
                "Expected type(trapezoid) = Trapezoid, instead found %s" % type(trapezoid).__name__

            # Replace trapezoid with four trapezoids
            # 1 -> 2 -> 3 -> 4
            # order is top to bottom, then left to right
            # 1: left of segment
            # 2: above segment
            # 3: below segment
            # 4: right of segment
            trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                             trapezoid.left_points,
                                             segment.endpoint1,
                                             trapezoid.bottom_segment)
            trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                             segment.endpoint1,
                                             segment.endpoint2,
                                             segment)
            trapezoid3 = trapclass.Trapezoid(segment,
                                             segment.endpoint1,
                                             segment.endpoint2,
                                             trapezoid.bottom_segment)
            trapezoid4 = trapclass.Trapezoid(trapezoid.top_segment,
                                             segment.endpoint2,
                                             trapezoid.right_points,
                                             trapezoid.bottom_segment)

            trap_node1 = dag.DagNode(trapezoid1)
            trap_node2 = dag.DagNode(trapezoid2)
            trap_node3 = dag.DagNode(trapezoid3)
            trap_node4 = dag.DagNode(trapezoid4)

            # Update DAG
            parent_nodes = node.parents

            if len(parent_nodes) == 0:
                if __debug__:
                    print("[VD] [Single trapezoid] replace initial bounding box")
                # Replace the initial bounding box
                # new root becomes left endpoint of segment
                self.dag = dag.DagNode(segment.endpoint1)
                self.dag.set_left_child(trap_node1)
                self.dag.set_right_child(dag.DagNode(segment.endpoint2))
                self.dag.right_child.set_right_child(trap_node4)
                self.dag.right_child.set_left_child(dag.DagNode(segment))
                self.dag.right_child.left_child.set_left_child(trap_node3)
                self.dag.right_child.left_child.set_right_child(trap_node2)
            else:
                node_to_set = dag.DagNode(segment.endpoint1)
                for parent_node in parent_nodes:
                    if parent_node.left_child.content == trapezoid:  # If we are the left child
                        parent_node.set_left_child(node_to_set)  # Left endpoint becomes left child
                        lp_node = parent_node.left_child  # Left Point node
                    else:
                        # We are the right child
                        parent_node.set_right_child(node_to_set)  # Left endpoint becomes right child
                        lp_node = parent_node.right_child

                lp_node.set_left_child(trap_node1)
                lp_node.set_right_child(dag.DagNode(segment.endpoint2))
                lp_node.right_child.set_right_child(trap_node4)
                lp_node.right_child.set_left_child(dag.DagNode(segment))
                segment_node = lp_node.right_child.left_child
                segment_node.set_left_child(trap_node3)
                segment_node.set_right_child(trap_node2)

            # Update neighbour lists
            trap_node1.left_neighbours = node.left_neighbours[:]
            trap_node1.right_neighbours = [trap_node2, trap_node3]
            for left_neighbour in trap_node1.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

            trap_node2.left_neighbours = [trap_node1]
            trap_node2.right_neighbours = [trap_node4]

            trap_node3.left_neighbours = [trap_node1]
            trap_node3.right_neighbours = [trap_node4]

            trap_node4.left_neighbours = [trap_node2, trap_node3]
            trap_node4.right_neighbours = node.right_neighbours[:]
            for right_neighbour in trap_node4.right_neighbours:
                for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                    if left_neighbour == node:
                        right_neighbour.left_neighbours[left_neighbour_index] = trap_node4

        else:
            carry = None
            carry_complement = None
            for node in nodes:
                trapezoid = node.content

                assert isinstance(trapezoid, trapclass.Trapezoid), \
                    "Expected type(trapezoid) = Trapezoid, instead found %s" % type(trapezoid).__name__

                # Left most intersection trapezoid
                if trapezoid.contains(segment.endpoint1) and segment.endpoint1.x_order(trapezoid.left_points[0]) != 0:

                    if __debug__:
                        print("Handling left most trapezoid intersection...")

                    right_points_above_segment = [point for point in trapezoid.right_points
                                                  if point.is_above(segment)]
                    right_points_below_segment = [point for point in trapezoid.right_points
                                                  if point.is_below(segment)]

                    # Replace trapezoid with three trapezoids
                    # 1 -> 2 -> 3
                    # order is top to bottom, then left to right
                    # 1: left of segment
                    # 2: above segment
                    # 3: below segment
                    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment, trapezoid.left_points, segment.endpoint1,
                                                     trapezoid.bottom_segment)
                    trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment, segment.endpoint1,
                                                     right_points_above_segment, segment)
                    trapezoid3 = trapclass.Trapezoid(segment, segment.endpoint1, right_points_below_segment,
                                                     trapezoid.bottom_segment)

                    trap_node1 = dag.DagNode(trapezoid1)
                    trap_node2 = dag.DagNode(trapezoid2)
                    trap_node3 = dag.DagNode(trapezoid3)

                    if not trapezoid2.right_points:
                        carry = trap_node2
                    elif not trapezoid3.right_points:
                        carry = trap_node3

                    # Update DAG
                    parent_nodes = node.parents

                    assert parent_nodes is not [], "Case parent_node = None not implemented"

                    node_to_set = dag.DagNode(segment.endpoint1)
                    for parent_node in parent_nodes:
                        if parent_node.left_child.content == trapezoid:
                            parent_node.set_left_child(node_to_set)
                            lp_node = parent_node.left_child
                        else:
                            parent_node.set_right_child(node_to_set)
                            lp_node = parent_node.right_child

                    lp_node.set_left_child(trap_node1)
                    lp_node.set_right_child(dag.DagNode(segment))
                    segment_node = lp_node.right_child
                    segment_node.set_left_child(trap_node3)
                    segment_node.set_right_child(trap_node2)

                    trap_node1 = lp_node.left_child
                    trap_node2 = segment_node.right_child
                    trap_node3 = segment_node.left_child

                    # Update neighbour lists
                    trap_node1.left_neighbours = node.left_neighbours[:]
                    trap_node1.right_neighbours = [trap_node2, trap_node3]
                    for left_neighbour in trap_node1.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

                    trap_node2.left_neighbours = [trap_node1]
                    if carry == trap_node2:
                        trap_node2.right_neighbours = []
                    else:
                        trap_node2.right_neighbours = [t for t in node.right_neighbours if
                                                       len([point for point in t.content.left_points if
                                                            point.is_above(segment)]) > 0]
                    for right_neighbour in trap_node2.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

                    trap_node3.left_neighbours = [trap_node1]
                    if carry == trap_node3:
                        trap_node3.right_neighbours = []
                    else:
                        trap_node3.right_neighbours = [t for t in node.right_neighbours if
                                                       len([point for point in t.content.left_points if
                                                            point.is_below(segment)]) > 0]

                    for right_neighbour in trap_node3.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node3
                            elif left_neighbour == trap_node2:
                                right_neighbour.left_neighbours.append(trap_node3)  # net toegevoegd




                    assert self.trap_segs_valid(), "traaaa"
                    assert trap_node1.content.left_points, "n1"
                    assert trap_node2.content.left_points, "n2"
                    assert trap_node3.content.left_points, "n3"
                    assert self.no_dupe(self.dag), 'oeir'
                    assert self.all_child(self.dag), "oeoeiea"

                    assert self.all_valid(), "n1"
                    if __debug__:
                        if not self.all_allowed_neighbours():
                            test_draw.test_draw_dag(self.dag)
                            test_draw.test_draw_segment(segment)
                            plt.show()
                            assert False, "ehao"



                # Right most intersection trapezoid
                elif trapezoid.contains(segment.endpoint2) and segment.endpoint2.x_order(trapezoid.right_points[0]) != 0:

                    if __debug__:
                        print("Handling right most trapezoid intersection...")

                    left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
                    left_points_below_segment = [point for point in trapezoid.left_points if
                                                 point.is_below(segment)]

                    assert carry is not None if not left_points_below_segment or not left_points_above_segment \
                        else carry is None, "VD: Expected a carry, but none found"

                    # Replace trapezoid with three trapezoids
                    # 1 -> 2 -> 3
                    # order is top to bottom, then left to right
                    # 1: above segment
                    # 2: below segment
                    # 3: right of segment
                    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment, left_points_above_segment,
                                                     segment.endpoint2, segment)
                    trapezoid2 = trapclass.Trapezoid(segment, left_points_below_segment, segment.endpoint2,
                                                     trapezoid.bottom_segment)
                    trapezoid3 = trapclass.Trapezoid(trapezoid.top_segment, segment.endpoint2, trapezoid.right_points,
                                                     trapezoid.bottom_segment)

                    trap_node1 = dag.DagNode(trapezoid1)
                    trap_node2 = dag.DagNode(trapezoid2)
                    trap_node3 = dag.DagNode(trapezoid3)

                    # Update neighbour lists
                    if carry is not None and not left_points_above_segment:
                        trap_node1.left_neighbours = carry.left_neighbours[:]
                        trap_node1.content.update_left_points(carry.content.left_points)

                        # Update reference to carry to refer to trap_node1
                        for carry_left_neighbour in carry.left_neighbours:
                            for (right_neighbour_index, right_neighbour) in \
                                    enumerate(carry_left_neighbour.right_neighbours):
                                if right_neighbour == carry:
                                    carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node1
                    else:
                        trap_node1.left_neighbours = [t for t in node.left_neighbours if
                                                      len([point for point in t.content.right_points if
                                                           point.is_above(segment)]) > 0]
                    trap_node1.right_neighbours = [trap_node3]
                    for left_neighbour in trap_node1.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

                    if carry is not None and not left_points_below_segment:
                        trap_node2.left_neighbours = carry.left_neighbours[:]
                        trap_node2.content.update_left_points(carry.content.left_points)

                        # Update reference to carry to refer to trap_node1
                        for carry_left_neighbour in carry.left_neighbours:
                            for (right_neighbour_index, right_neighbour) in \
                                    enumerate(carry_left_neighbour.right_neighbours):
                                if right_neighbour == carry:
                                    carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
                    else:
                        trap_node2.left_neighbours = [t for t in node.left_neighbours if
                                                      len([point for point in t.content.right_points if
                                                           point.is_below(segment)]) > 0]
                    trap_node2.right_neighbours = [trap_node3]
                    for left_neighbour in trap_node2.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
                            #edge case where both trap1 and trap2 become neighbours of the trapezoid in question
                            elif right_neighbour == trap_node1:
                                left_neighbour.right_neighbours.append(trap_node2) #net toegevoegd

                    trap_node3.left_neighbours = [trap_node1, trap_node2]
                    trap_node3.right_neighbours = node.right_neighbours
                    for right_neighbour in trap_node3.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node3

                    # Update DAG
                    parent_nodes = node.parents
                    node_to_set = dag.DagNode(segment.endpoint2)
                    for parent_node in parent_nodes:
                        if parent_node.left_child == node:
                            parent_node.set_left_child(node_to_set)
                 #           assert lp_node is parent_node.left_child if parent_node else True
                            lp_node = parent_node.left_child
                        else:
                            parent_node.set_right_child(node_to_set)
                  #          assert lp_node is parent_node.right_child if parent_node else True
                            lp_node = parent_node.right_child

                    lp_node.set_right_child(trap_node3)
                    lp_node.set_left_child(dag.DagNode(segment))
                    segment_node = lp_node.left_child
                    segment_node.set_left_child(trap_node2)
                    segment_node.set_right_child(trap_node1)

                    # Update dag references to carry
                    if carry is not None:
                        if not left_points_above_segment:
                            carry_complement = trap_node1
                        if not left_points_below_segment:
                            carry_complement = trap_node2


                        for parent in carry.parents:
                            if parent.left_child == carry:
                                parent.set_left_child(carry_complement)
                            else:
                                parent.set_right_child(carry_complement)

                    assert trap_node1.content.left_points, "n1"
                    assert trap_node2.content.left_points, "n2"
                    assert trap_node3.content.left_points, "n3"
                    assert self.trap_segs_valid(), "traaaa"
                    if __debug__ and not self.all_child(self.dag):
                        test_draw.test_draw_dag(self.dag)
                 #       test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "aiiia"
                    assert self.no_dupe(self.dag), 'oeir'
                    if __debug__ and not self.all_allowed_neighbours():
                        test_draw.test_draw_dag(self.dag)
                        test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "boab"
                    if __debug__ and not self.all_valid():
                        test_draw.test_draw_dag(self.dag)
                        test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "ehao"


                else:  # Trapezoid is separated by segment

                    if __debug__:
                        print("Handling intermediate trapezoid intersection...")

                    left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
                    left_points_below_segment = [point for point in trapezoid.left_points if
                                                 point.is_below(segment)]
                    right_points_above_segment = [point for point in trapezoid.right_points if point.is_above(segment)]
                    right_points_below_segment = [point for point in trapezoid.right_points if
                                                  point.is_below(segment)]

                    assert carry is not None if not left_points_below_segment or not left_points_above_segment \
                        else carry is None, "VD: Expected a carry, but none found"

                    # Replace trapezoid with two trapezoids
                    # 1 -> 2
                    # order is top to bottom, then left to right
                    # 1: above segment
                    # 2: below segment
                    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment, left_points_above_segment,
                                                     right_points_above_segment, segment)
                    trapezoid2 = trapclass.Trapezoid(segment, left_points_below_segment, right_points_below_segment,
                                                     trapezoid.bottom_segment)

                    trap_node1 = dag.DagNode(trapezoid1)
                    trap_node2 = dag.DagNode(trapezoid2)

                    # Update left neighbour lists
                    if carry is not None and not left_points_above_segment:
                        trap_node1.left_neighbours = carry.left_neighbours[:]
                        trap_node1.content.update_left_points(carry.content.left_points)

                        # Update reference to carry to refer to trap_node1
                        for carry_left_neighbour in carry.left_neighbours:
                            for (right_neighbour_index, right_neighbour) in \
                                    enumerate(carry_left_neighbour.right_neighbours):
                                if right_neighbour == carry:
                                    carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node1
                    else:
                        trap_node1.left_neighbours = [t for t in node.left_neighbours if
                                                      len([point for point in t.content.right_points if
                                                           point.is_above(segment)]) > 0]
                    for left_neighbour in trap_node1.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

                    if carry is not None and not left_points_below_segment:
                        trap_node2.left_neighbours = carry.left_neighbours[:]
                        trap_node2.content.update_left_points(carry.content.left_points)

                        # Update reference to carry to refer to trap_node1
                        for carry_left_neighbour in carry.left_neighbours:
                            for (right_neighbour_index, right_neighbour) in \
                                    enumerate(carry_left_neighbour.right_neighbours):
                                if right_neighbour == carry:
                                    carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
                    else:
                        trap_node2.left_neighbours = [t for t in node.left_neighbours if
                                                      len([point for point in t.content.right_points if
                                                           point.is_below(segment)]) > 0]
                    for left_neighbour in trap_node2.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
                            #edge case where both trap1 and trap2 become neighbours of the trapezoid in question
                            elif right_neighbour == trap_node1:
                                left_neighbour.right_neighbours.append(trap_node2)


                    # Update dag references to carry
                    if carry is not None:
                        if not left_points_above_segment:
                            carry_complement = trap_node1
                        if not left_points_below_segment:
                            carry_complement = trap_node2

                        for parent in carry.parents:
                             if parent.left_child == carry:
                                parent.set_left_child(carry_complement)
                             else:
                                parent.set_right_child(carry_complement)
                        carry.reset_parent()

                    # Update carry
                    if not trapezoid1.right_points:
                        carry = trap_node1
                    elif not trapezoid2.right_points:
                        carry = trap_node2
                    else:
                        carry = None

                    # Update right neighbour lists
                    if carry == trap_node1:
                        trap_node1.right_neighbours = []
                    else:
                        trap_node1.right_neighbours = [t for t in node.right_neighbours if
                                                       len([point for point in t.content.left_points if
                                                            point.is_above(segment)]) > 0]
                    for right_neighbour in trap_node1.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node1

                    if carry == trap_node2:
                        trap_node2.right_neighbours = []
                    else:
                        trap_node2.right_neighbours = [t for t in node.right_neighbours if
                                                       len([point for point in t.content.left_points if
                                                            point.is_below(segment)]) > 0]

                    for right_neighbour in trap_node2.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node2
                            #edge case where both trap1 and trap2 become neighbours of the trapezoid in question
                            elif left_neighbour == trap_node1:
                                right_neighbour.left_neighbours.append(trap_node2)

                    # Update DAG
                    parent_nodes = node.parents
                    node_to_set = dag.DagNode(segment)
                    for parent_node in parent_nodes:
                        if parent_node.left_child == node:
                            parent_node.set_left_child(node_to_set)
                            lp_node = parent_node.left_child
                        else:
                            parent_node.set_right_child(node_to_set)
                            lp_node = parent_node.right_child

                    lp_node.set_right_child(trap_node1)
                    lp_node.set_left_child(trap_node2)

                    assert trap_node1.content.left_points, "n1"
                    assert trap_node2.content.left_points, 'n2'
                    if __debug__ and not self.trap_segs_valid():
                        test_draw.test_draw_dag(self.dag)
                     #   test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "traaaa"
                    assert self.all_child(self.dag), "oeoeiea"
                    if __debug__ and not self.no_dupe(self.dag):
                        test_draw.test_draw_dag(self.dag)
                        test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "oeir"
                    if __debug__ and not  self.all_valid():
                        test_draw.test_draw_dag(self.dag)
                        test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "area"
                    if __debug__ and not self.all_allowed_neighbours():
                        test_draw.test_draw_dag(self.dag)
                        test_draw.test_draw_segment(segment)
                        plt.show()
                        assert False, "ehao"


                assert not self.dag.find_all_node(node), "Reference to old trapezoid detected"

    def trap_node_list(self, node):
        if node is None:
            return []
        elif isinstance(node.content, trapclass.Trapezoid):
            return [node]
        else:
            return self.trap_node_list(node.left_child) + self.trap_node_list(node.right_child)

    def valid_node(self, node):
        trapl = self.trap_node_list(self.dag)
        if not isinstance(node.content, trapclass.Trapezoid):
            return True
        for nb in node.right_neighbours:
            if not nb in trapl:
                return False
        for nb in node.left_neighbours:
            if not nb in trapl:
                return False
        return node in trapl

    def all_valid(self):
        trapl = self.trap_node_list(self.dag)
        for node in trapl:
            if not self.valid_node(node):
                return False
        return True

    def no_dupe(self, node):
        if isinstance(node.content, trapclass.Trapezoid):
            return True
        else:
            b1 = not node.left_child is node.right_child
            return self.no_dupe(node.left_child) and self.no_dupe(node.right_child) and b1

    def single_trap_segs_valid(self, trap_node):
        if len(trap_node.content.left_points) > 0:
            if trap_node.content.left_points[0].x != trap_node.content.left_segment.endpoint1.x:
                return False

        if len(trap_node.content.right_points) > 0:
            if trap_node.content.right_points[0].x != trap_node.content.right_segment.endpoint1.x:
                return False
        return True

    def trap_segs_valid(self):
        trapl = self.trap_node_list(self.dag)
        for trap_node in trapl:
            if not self.single_trap_segs_valid(trap_node):
                return False
        return True

    def all_child(self, node):
        if isinstance(node.content, trapclass.Trapezoid):
            return True
        else:
            if not node.left_child or not node.right_child:
                return False
            return self.all_child(node.left_child) and self.all_child(node.right_child)

    def allowed_neighbours(self, node):
        for nb in node.right_neighbours:
            check = False
            for point in node.content.right_points:
                if point in nb.content.left_points:
                    check = True
                    break
            if not check:
                return False
        for nb in node.left_neighbours:
            check = False
            for point in node.content.left_points:
                if point in nb.content.right_points:
                    check = True
                    break
            if not check:
                return False
        return True

    def got_all_neighbours(self, node):
        trapl = self.trap_node_list(self.dag)
        for nb in trapl:
            if not nb is node:
                for point in node.content.right_points:
                    if point in nb.content.left_points:
                        if nb not in node.right_neighbours:
                            return False
                for point in node.content.left_points:
                    if point in nb.content.right_points:
                        if nb not in node.left_neighbours:
                            return False

        return True

    def all_allowed_neighbours(self):
        trapl = self.trap_node_list(self.dag)
        for trap_node in trapl:
            if not self.allowed_neighbours(trap_node) or not self.got_all_neighbours(trap_node):
                return False
        return True


