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
            if current_node.right_neighbours == []:
                test_draw.test_draw_dag(self.dag)
               # test_draw.test_draw_segment(segment)
                plt.show()
                print("oh")
            assert current_node.right_neighbours != [], "Current node has no neighbours, but is not end node"
            # Go to the next trapezoid on the path
            # assert len([n for n in current_node.right_neighbours if n.content.segment_enter(segment)]) > 0, "will get stuck"
            temp = [n for n in current_node.right_neighbours if n.content.segment_enter(segment)]
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
        if len(nodes) == 1:
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
            parent_node = node.parent

            if parent_node is None:
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
                if parent_node.left_child.content == trapezoid:  # If we are the left child
                    parent_node.set_left_child(dag.DagNode(segment.endpoint1))  # Left endpoint becomes left child
                    lp_node = parent_node.left_child  # Left Point node
                else:
                    # We are the right child
                    parent_node.set_right_child(dag.DagNode(segment.endpoint1))  # Left endpoint becomes right child
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
                if trapezoid.contains(segment.endpoint1):
                    print("Handling left most trapezoid intersection...")
                    right_points_above_segment = [point for point in trapezoid.right_points
                                                  if point.is_above(segment)]
                    right_points_below_segment = [point for point in trapezoid.right_points
                                                  if not point.is_above(segment)]

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
                    parent_node = node.parent

                    assert parent_node is not None, "Case parent_node = None not implemented"

                    if parent_node.left_child.content == trapezoid:
                        parent_node.set_left_child(dag.DagNode(segment.endpoint1))
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right_child(dag.DagNode(segment.endpoint1))
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
                                                            not point.is_above(segment)]) > 0]
                    for right_neighbour in trap_node3.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node3

                # Right most intersection trapezoid
                elif trapezoid.contains(segment.endpoint2) and segment.endpoint2.x != trapezoid.right_segment.endpoint1.x:
                    print("Handling right most trapezoid intersection...")
                    left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
                    left_points_below_segment = [point for point in trapezoid.left_points if
                                                 not point.is_above(segment)]

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

                        # Update reference to carry to refer to trap_node1
                        for carry_left_neighbour in carry.left_neighbours:
                            for (right_neighbour_index, right_neighbour) in \
                                    enumerate(carry_left_neighbour.right_neighbours):
                                if right_neighbour == carry:
                                    carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
                    else:
                        trap_node2.left_neighbours = [t for t in node.left_neighbours if
                                                      len([point for point in t.content.right_points if
                                                           not point.is_above(segment)]) > 0]
                    trap_node2.right_neighbours = [trap_node3]
                    for left_neighbour in trap_node2.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node2

                    trap_node3.left_neighbours = [trap_node1, trap_node2]
                    trap_node3.right_neighbours = node.right_neighbours
                    for right_neighbour in trap_node3.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node3

                    # Update DAG
                    parent_node = node.parent
                    if parent_node.left_child == node:
                        parent_node.set_left_child(dag.DagNode(segment.endpoint2))
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right_child(dag.DagNode(segment.endpoint2))
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

                        for to_update in self.dag.find_all_node(carry):
                            if to_update.parent.left_child == to_update:
                                to_update.parent.set_left_child(carry_complement)
                            else:
                                to_update.parent.set_right_child(carry_complement)

                else:  # Trapezoid is separated by segment
                    print("Handling intermediate trapezoid intersection...")
                    left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
                    left_points_below_segment = [point for point in trapezoid.left_points if
                                                 not point.is_above(segment)]
                    right_points_above_segment = [point for point in trapezoid.right_points if point.is_above(segment)]
                    right_points_below_segment = [point for point in trapezoid.right_points if
                                                  not point.is_above(segment)]

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

                        # Update reference to carry to refer to trap_node1
                        for carry_left_neighbour in carry.left_neighbours:
                            for (right_neighbour_index, right_neighbour) in \
                                    enumerate(carry_left_neighbour.right_neighbours):
                                if right_neighbour == carry:
                                    carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
                    else:
                        trap_node2.left_neighbours = [t for t in node.left_neighbours if
                                                      len([point for point in t.content.right_points if
                                                           not point.is_above(segment)]) > 0]
                    for left_neighbour in trap_node2.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node2

                    # Update dag references to carry
                    if carry is not None:
                        if not left_points_above_segment:
                            carry_complement = trap_node1
                        if not left_points_below_segment:
                            carry_complement = trap_node2

                        for to_update in self.dag.find_all_node(carry):
                            if to_update.parent.left_child == to_update:
                                to_update.parent.set_left_child(carry_complement)
                            else:
                                to_update.parent.set_right_child(carry_complement)

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
                                                            point.is_above(segment)]) > 0]
                    for right_neighbour in trap_node2.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in right_neighbour.left_neighbours:
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

                    # Update DAG
                    parent_node = node.parent
                    if parent_node.left_child == node:
                        parent_node.set_left_child(dag.DagNode(segment))
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right_child(dag.DagNode(segment))
                        lp_node = parent_node.right_child

                    lp_node.set_right_child(trap_node1)
                    lp_node.set_left_child(trap_node2)

                assert not self.dag.find_all_node(node), "Reference to old trapezoid detected"

import geometry
import segment, vertex
#testing
nodes = [(1,1), (10,10)]
vertices = [vertex.Vertex(2,5), vertex.Vertex(8,6), vertex.Vertex(1,2), vertex.Vertex(3,4)]

seg = segment.Segment(vertices[0], vertices[1])
seg2 = segment.Segment(vertices[2], vertices[1])
seg3 = segment.Segment(vertices[2], vertex.Vertex(7, 2))
vd = VerticalDecomposition(geometry.find_bounding_box(nodes))
vd.add_segment(seg)
vd.add_segment(seg2)
vd.add_segment(seg3)
test_draw.test_draw_dag(vd.dag)
plt.show()
