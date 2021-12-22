import dagnode as dag
import trapezoid as trapclass



# Class that represents the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        self.dag = dag.DagNode(bounding_box, None, None, None)

    # Finds and returns the trapezoid in which the requested point lies in associated DAG node
    def find_point_location(self, point):
        current_node = self.dag.choose_next(point)
        while not isinstance(current_node.content, trapclass.Trapezoid):
            current_node = current_node.choose_next(point)
        assert isinstance(current_node.content, trapclass.Trapezoid), "Expected to find type(current_node.content) = Trapezoid, instead found %s" % type(current_node.content).__name__
        return current_node #return DAG node containing trapezoid

    # Finds all trapezoids that intersect the segment
    def find_intersecting_trapezoids(self, segment):
        start_node = self.find_point_location(segment.endpoint1)
        end_node = self.find_point_location(segment.endpoint2)
        print(start_node)
        print(end_node)
        intersected_trapezoids = [start_node]
        current_node = start_node
        while not current_node == end_node:
            # Go to the next trapezoid on the path
            for node in current_node.right_neighbours:
                trap = node.content
                assert isinstance(trap, trapclass.Trapezoid), "expected type(trap) = Trapezoid, found %s" % type(trap).__name__
                if trap.intersects_segment(segment):
                    # Found the successor
                    intersected_trapezoids.append(node)
                    current_node = node
                    break

        return intersected_trapezoids

    # Adds a new segment to the vertical decomposition if it does not intersect
    # Returns True if segment could be inserted in this vertical decomposition
    #         False if segment could not be inserted in this vertical decomposition
    def add_segment(self, segment):
        print("Adding segments")
        intersecting_trapezoids = self.find_intersecting_trapezoids(segment)
        print("Found intersecting trapezoids")

        intersection_found = False
        for node in intersecting_trapezoids:
            trapezoid = node.content
            assert isinstance(trapezoid, trapclass.Trapezoid), "Expected type(trapezoid) = Trapezoid, instead found %s" % type(trapezoid).__name__
            # Checks if the segment has an intersection with the bottom segment of the trapezoid
            if trapezoid.find_intersection(segment):
                intersection_found = True

        if intersection_found:
            return False

        # Add segment to DAG
        self.update(intersecting_trapezoids, segment)
        return True

    # Updates the DAG with the new trapezoids induced by adding segment
    def update(self, nodes, segment):
        if len(nodes) == 1:
            print("Segment entirely contained in a single trapezoid")
            # Segment is completely contained in a single trapezoid
            node = nodes[0]
            trapezoid = node.content

            assert isinstance(trapezoid, trapclass.Trapezoid), "Expected type(trapezoid) = Trapezoid, instead found %s" % type(trapezoid).__name__

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
            trap_node1.left_neighbours = node.left_neighbours
            trap_node1.right_neighbours = [trap_node2, trap_node3]
            for left_neighbour in trap_node1.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

            trap_node1.left_neighbours = [trap_node1]
            trap_node2.right_neighbours = [trap_node4]

            trap_node3.left_neighbours = [trap_node1]
            trap_node3.right_neighbours = [trap_node4]

            trap_node4.left_neighbours = [trap_node2, trap_node3]
            trap_node4.right_neighbours = node.right_neighbours
            for right_neighbour in trap_node4.right_neighbours:
                for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                    if left_neighbour == node:
                        right_neighbour.left_neighbours[left_neighbour_index] = trap_node4

        else:
            print("Segment goes through multiple trapezoids...")
            carry = None
            for node in nodes:
                trapezoid = node.content

                assert isinstance(trapezoid, trapclass.Trapezoid),\
                    "Expected type(trapezoid) = Trapezoid, instead found %s" % type(trapezoid).__name__

                print("Calling contains on trapezoid???")
                if trapezoid.contains(segment.endpoint1):
                    right_points_above_segment = [point for point in trapezoid.right_points if point.is_above(segment)]
                    right_points_below_segment = [point for point in trapezoid.right_points if not point.is_above(segment)]

                    # Replace trapezoid with three trapezoids
                    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment, trapezoid.left_points, segment.endpoint1, trapezoid.bottom_segment)
                    trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment, segment.endpoint1, right_points_above_segment, segment)
                    trapezoid3 = trapclass.Trapezoid(segment, segment.endpoint1, right_points_below_segment, trapezoid.bottom_segment)

                    if not trapezoid2.right_points:
                        carry = trapezoid2
                    elif not trapezoid3.right_points:
                        carry = trapezoid3

                    # Update DAG
                    parent_node = trapezoid.parent

                    assert parent_node is not None, "Case parent_node = None not implemented"

                    if parent_node.left_child.content == trapezoid:
                        parent_node.set_left_child(segment.endpoint1)
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right(segment.endpoint1)
                        lp_node = parent_node.right_child

                    lp_node.set_left_child(trapezoid1)
                    lp_node.set_right_child(segment)
                    segment_node = lp_node.right_child
                    segment_node.set_left_child(trapezoid3)
                    segment_node.set_right_child(trapezoid2)

                    trap_node1 = lp_node.left_child
                    trap_node2 = segment_node.right_child
                    trap_node3 = segment_node.left_child

                    # @TODO: Neighbours moeten naar nodes en niet trapezoids
                    # Update neighbour lists
                    trapezoid1.left_neighbours = trapezoid.left_neighbours
                    trapezoid1.right_neighbours = [trap_node2, trap_node3]
                    for left_neighbour in trapezoid1.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in left_neighbour.right_neighbours:
                            if right_neighbour == node:
                                left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

                    trapezoid2.left_neighbours = [trap_node1]
                    if carry == trapezoid2:
                        trapezoid2.right_neighbours = []
                    else:
                        trapezoid2.right_neighbours = [t for t in trapezoid.right_neighbours if len([point for point in t.left_points if point.is_above(segment)]) > 0]
                    for right_neighbour in trapezoid2.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in right_neighbour.left_neighbours:
                            if left_neighbour == node:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

                    trapezoid3.left_neighbours = [trap_node1]
                    if carry == trapezoid3:
                        trapezoid3.right_neighbours = []
                    else:
                        trapezoid3.right_neighbours = [t for t in trapezoid.right_neighbours if len([point for point in t.left_points if not point.is_above(segment)]) > 0]
                    for right_neighbour in trapezoid3.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in right_neighbour.left_neighbours:
                            if left_neighbour == trapezoid:
                                right_neighbour.left_neighbours[left_neighbour_index] = trap_node3



                elif trapezoid.contains(segment.endpoint2):
                    left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
                    left_points_below_segment = [point for point in trapezoid.left_points if not point.is_above(segment)]

                    assert carry is not None if not left_points_below_segment or not left_points_above_segment else carry is None, "VD: Expected a carry, but none found"


                    # Replace trapezoid with three trapezoids
                    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment, left_points_above_segment, segment.endpoint2, segment)
                    trapezoid2 = trapclass.Trapezoid(segment, left_points_below_segment, segment.endpoint2, trapezoid.bottom_segment)
                    trapezoid3 = trapclass.Trapezoid(trapezoid.top_segment, segment.endpoint2, trapezoid.right_points, trapezoid.bottom_segment)

                    # @TODO: Neighbours moeten naar nodes en niet trapezoids
                    # Update neighbour lists
                    if carry is not None and not left_points_above_segment:
                        trapezoid1.left_neighbours = carry.left_neighbours
                    else:
                        trapezoid1.left_neighbours = [t for t in trapezoid.left_neighbours if len([point for point in t.right_points if point.is_above(segment)]) > 0]
                    trapezoid1.right_neighbours = [trapezoid3]
                    for left_neighbour in trapezoid1.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in left_neighbour.right_neighbours:
                            if right_neighbour == trapezoid:
                                left_neighbour.right_neighbours[right_neighbour_index] = trapezoid1

                    if carry is not None and not left_points_below_segment:
                        trapezoid2.left_neighbours = carry.left_neighbours
                    else:
                        trapezoid2.left_neighbours = [t for t in trapezoid.left_neighbours if len([point for point in t.right_points if not point.is_above(segment)]) > 0]
                    trapezoid2.right_neighbours = [trapezoid3]
                    for left_neighbour in trapezoid2.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in left_neighbour.right_neighbours:
                            if right_neighbour == trapezoid:
                                left_neighbour.right_neighbours[right_neighbour_index] = trapezoid2

                    trapezoid3.left_neighbours = [trapezoid1, trapezoid2]
                    trapezoid3.right_neighbours = trapezoid.right_neighbours
                    for right_neighbour in trapezoid3.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in right_neighbour.left_neighbours:
                            if left_neighbour == trapezoid:
                                right_neighbour.left_neighbours[left_neighbour_index] = trapezoid3

                    # Update DAG
                    parent_node = trapezoid.parent
                    if parent_node.left_child.content == trapezoid:
                        parent_node.set_left_child(segment.endpoint2)
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right(segment.endpoint2)
                        lp_node = parent_node.right_child

                    lp_node.set_right_child(trapezoid3)
                    lp_node.set_left_child(segment)
                    segment_node = lp_node.left_child
                    segment_node.set_left_child(trapezoid2)
                    segment_node.set_right_child(trapezoid1)
                else:  # Trapezoid is separated by segment
                    left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
                    left_points_below_segment = [point for point in trapezoid.left_points if not point.is_above(segment)]
                    right_points_above_segment = [point for point in trapezoid.right_points if point.is_above(segment)]
                    right_points_below_segment = [point for point in trapezoid.right_points if not point.is_above(segment)]

                    assert carry is not None if not left_points_below_segment or not left_points_above_segment else carry is None, "VD: Expected a carry, but none found"

                    # Replace trapezoid with two trapezoids
                    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment, left_points_above_segment, right_points_above_segment, segment)
                    trapezoid2 = trapclass.Trapezoid(segment, left_points_below_segment, right_points_below_segment, trapezoid.bottom_segment)

                    # @TODO: Neighbours moeten naar nodes en niet trapezoids
                    # Update left neighbour lists
                    if carry is not None and not left_points_above_segment:
                        trapezoid1.left_neighbours = carry.left_neighbours
                    else:
                        trapezoid1.left_neighbours = [t for t in trapezoid.left_neighbours if len([point for point in t.right_points if point.is_above(segment)]) > 0]
                    for left_neighbour in trapezoid1.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in left_neighbour.right_neighbours:
                            if right_neighbour == trapezoid:
                                left_neighbour.right_neighbours[right_neighbour_index] = trapezoid1

                    if carry is not None and not left_points_below_segment:
                        trapezoid2.left_neighbours = carry.left_neighbours
                    else:
                        trapezoid2.left_neighbours = [t for t in trapezoid.left_neighbours if len([point for point in t.right_points if not point.is_above(segment)]) > 0]
                    for left_neighbour in trapezoid2.left_neighbours:
                        for (right_neighbour_index, right_neighbour) in left_neighbour.right_neighbours:
                            if right_neighbour == trapezoid:
                                left_neighbour.right_neighbours[right_neighbour_index] = trapezoid2

                    # Update carry
                    if not trapezoid1.right_points:
                        carry = trapezoid1
                    elif not trapezoid2.right_points:
                        carry = trapezoid2
                    else:
                        carry = None

                    # @TODO: Neighbours moeten naar nodes en niet trapezoids
                    # Update right neighbour lists
                    if carry == trapezoid1:
                        trapezoid1.right_neighbours = []
                    else:
                        trapezoid1.right_neighbours = [t for t in trapezoid.right_neighbours if len([point for point in t.left_points if point.is_above(segment)]) > 0]
                    for right_neighbour in trapezoid1.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in right_neighbour.left_neighbours:
                            if left_neighbour == trapezoid:
                                right_neighbour.left_neighbours[left_neighbour_index] = trapezoid1

                    if carry == trapezoid2:
                        trapezoid2.right_neighbours = []
                    else:
                        trapezoid2.right_neighbours = [t for t in trapezoid.right_neighbours if len([point for point in t.left_points if point.is_above(segment)]) > 0]
                    for right_neighbour in trapezoid2.right_neighbours:
                        for (left_neighbour_index, left_neighbour) in right_neighbour.left_neighbours:
                            if left_neighbour == trapezoid:
                                right_neighbour.left_neighbours[left_neighbour_index] = trapezoid2

                    # Update DAG
                    parent_node = trapezoid.parent
                    if parent_node.left_child.content == trapezoid:
                        parent_node.set_left_child(segment)
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right(segment)
                        lp_node = parent_node.right_child

                    lp_node.set_right_child(trapezoid1)
                    lp_node.set_left_child(trapezoid2)

