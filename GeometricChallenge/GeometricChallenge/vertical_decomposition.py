from __future__ import annotations
from typing import Tuple
import dagnode as dag
import trapezoid as trapclass
import segment as segclass
import vertex as vertclass


# Class that represents the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        self.dag = dag.DagNode(bounding_box)

    # @TODO: method verwijderen als alles werkt (wordt gebruikt voor debugging/tekenen)
    # Finds and returns the trapezoid in which the requested point lies in associated DAG node
    def find_point_location(self, point: vertclass.Vertex) -> dag.DagNode:
        current_node = self.dag.choose_next(point)

        while not isinstance(current_node.content, trapclass.Trapezoid):
            current_node = current_node.choose_next(point)

        return current_node  # Return DAG node containing trapezoid

    def point_location_segment(self, segment: segclass.Segment) -> [dag.DagNode]:
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
    def find_intersecting_trapezoids(self, segment: segclass.Segment) -> [dag.DagNode]:
        start_node, end_node = self.point_location_segment(segment)
        intersected_trapezoids = [start_node]
        current_node = start_node

        while current_node is not end_node:
            if len(current_node.right_neighbours) == 0 or not segment.intersects(current_node.content.right_segment):
                return []

            for node in current_node.right_neighbours:
                trap = node.content
                if trap.segment_enter(segment):
                    # Found the successor
                    intersected_trapezoids.append(node)
                    current_node = node
                    break
            else:
                # If no right neighbours found, then break while loop and return empty list
                return []

        return intersected_trapezoids

    # Adds a new segment to the vertical decomposition if it does not intersect
    # Returns True if segment could be inserted in this vertical decomposition
    #         False if segment could not be inserted in this vertical decomposition
    def add_segment(self, segment: segclass.Segment) -> bool:
        traps = self.find_intersecting_trapezoids(segment)

        if len(traps) == 0:
            return False

        # Add segment to DAG
        self.update(traps, segment)

        return True

    # Updates the DAG with the new trapezoids induced by adding segment
    def update(self, nodes: [dag.DagNode], segment: segclass.Segment) -> None:
        if len(nodes) == 1:
            self.update_single_trapezoid(nodes, segment)
        else:
            self.update_multiple_trapezoids(nodes, segment)

    def update_single_trapezoid(self, nodes: [dag.DagNode], segment: segclass.Segment) -> None:
        # Segment is completely contained in a single trapezoid
        node = nodes[0]
        trapezoid = node.content

        if not trapezoid.left_segment.on_segment(segment.endpoint1) \
                and not trapezoid.right_segment.on_segment(segment.endpoint2):
            self.update_single_trapezoid_contained(node, trapezoid, segment)

        if not trapezoid.left_segment.on_segment(segment.endpoint1) \
                and trapezoid.right_segment.on_segment(segment.endpoint2):
            self.update_single_trapezoid_right_boundary(node, trapezoid, segment)

    def update_single_trapezoid_contained(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment
    ) -> None:
        # 1: left of segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         trapezoid.left_points,
                                         segment.endpoint1,
                                         trapezoid.bottom_segment)
        # 2: above segment
        trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                         segment.endpoint1,
                                         segment.endpoint2,
                                         segment)
        # 3: below segment
        trapezoid3 = trapclass.Trapezoid(segment,
                                         segment.endpoint1,
                                         segment.endpoint2,
                                         trapezoid.bottom_segment)
        # 4: right of segment
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
            lp_node = dag.DagNode(segment.endpoint1)
            for parent_node in parent_nodes:
                if parent_node.left_child.content == trapezoid:  # If we are the left child
                    parent_node.set_left_child(lp_node)  # Left endpoint becomes left child
                else:
                    # We are the right child
                    parent_node.set_right_child(lp_node)  # Left endpoint becomes right child

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

    def update_single_trapezoid_right_boundary(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment
    ) -> None:
        right_points_above_segment = [point for point in trapezoid.right_points
                                      if point.is_above(segment)]
        right_points_below_segment = [point for point in trapezoid.right_points
                                      if point.is_below(segment)]

        # 1: left of segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         trapezoid.left_points,
                                         segment.endpoint1,
                                         trapezoid.bottom_segment)
        # 2: above segment
        trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                         segment.endpoint1,
                                         right_points_above_segment + [segment.endpoint2],
                                         segment)

        # 3: below segment
        trapezoid3 = trapclass.Trapezoid(segment,
                                         segment.endpoint1,
                                         right_points_below_segment + [segment.endpoint2],
                                         trapezoid.bottom_segment)

        trap_node1 = dag.DagNode(trapezoid1)
        trap_node2 = dag.DagNode(trapezoid2)
        trap_node3 = dag.DagNode(trapezoid3)

        # Update DAG
        parent_nodes = node.parents
        lp_node = dag.DagNode(segment.endpoint1)
        for parent_node in parent_nodes:
            if parent_node.left_child.content == trapezoid:  # If we are the left child
                parent_node.set_left_child(lp_node)  # Left endpoint becomes left child
            else:
                # We are the right child
                parent_node.set_right_child(lp_node)  # Left endpoint becomes right child

        # (Ruben vindt dat hier nog iets mee gedaan moet worden,
        # maar ik geloof er echt werkelijk waar helemaal niets van)
        lp_node.set_left_child(trap_node1)
        lp_node.set_right_child(dag.DagNode(segment.endpoint2))
        # lp_node.right_child.set_right_child(trap_node3)
        lp_node.right_child.set_left_child(dag.DagNode(segment))
        segment_node = lp_node.right_child.left_child
        segment_node.set_left_child(trap_node3)
        segment_node.set_right_child(trap_node2)

        # Update neighbours
        trap_node1.left_neighbours = node.left_neighbours[:]
        trap_node1.right_neighbours = [trap_node2, trap_node3]

        trap_node2.left_neighbours = [trap_node1]
        trap_node2.right_neighbours = [neighbour for neighbour in node.right_neighbours
                                       if neighbour.content.left_segment.intersects(trapezoid2.right_segment)]

        trap_node3.left_neighbours = [trap_node1]
        trap_node3.right_neighbours = [neighbour for neighbour in node.right_neighbours
                                       if neighbour.content.left_segment.intersects(trapezoid3.right_segment)]

        for left_neighbour in trap_node1.left_neighbours:
            for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                if right_neighbour == node:
                    left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

        for right_neighbour in trap_node2.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

        for right_neighbour in trap_node3.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node3

        # Add segment endpoint to neighbour trapezoids
        for right_neighbour in node.right_neighbours:
            if right_neighbour.content.left_segment.on_segment(segment.endpoint2):
                right_neighbour.content.left_points.append(segment.endpoint2)

    def update_single_trapezoid_both_boundary(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment
    ) -> None:
        left_points_above_segment = [point for point in trapezoid.left_points
                                     if point.is_above(segment)]
        left_points_below_segment = [point for point in trapezoid.left_points
                                     if point.is_below(segment)]
        right_points_above_segment = [point for point in trapezoid.right_points
                                      if point.is_above(segment)]
        right_points_below_segment = [point for point in trapezoid.right_points
                                      if point.is_below(segment)]

        # 1: above segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         left_points_above_segment + [segment.endpoint1],
                                         right_points_above_segment + [segment.endpoint2],
                                         segment)
        # 2: below segment
        trapezoid2 = trapclass.Trapezoid(segment,
                                         left_points_below_segment + [segment.endpoint1],
                                         right_points_below_segment + [segment.endpoint2],
                                         trapezoid.bottom_segment)

        trap_node1 = dag.DagNode(trapezoid1)
        trap_node2 = dag.DagNode(trapezoid2)

        # Update DAG
        parent_nodes = node.parents
        lp_node = dag.DagNode(segment.endpoint1)
        for parent_node in parent_nodes:
            if parent_node.left_child.content == trapezoid:  # If we are the left child
                parent_node.set_left_child(lp_node)  # Left endpoint becomes left child
            else:
                # We are the right child
                parent_node.set_right_child(lp_node)  # Left endpoint becomes right child

        # (Ruben vindt dat hier nog iets mee gedaan moet worden,
        # maar ik geloof er echt werkelijk waar helemaal niets van)
        # lp_node.set_left_child(trap_node1)
        lp_node.set_right_child(dag.DagNode(segment.endpoint2))
        # lp_node.right_child.set_right_child(trap_node4)
        lp_node.right_child.set_left_child(dag.DagNode(segment))
        segment_node = lp_node.right_child.left_child
        segment_node.set_left_child(trap_node2)
        segment_node.set_right_child(trap_node1)

        # Update neighbours
        trap_node1.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                      if left_neighbour.content.right_segment.intersects(trapezoid1.left_segment)]
        trap_node1.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                       if right_neighbour.content.left_segment.intersects(trapezoid1.right_segment)]

        trap_node2.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                      if left_neighbour.content.right_segment.intersects(trapezoid2.left_segment)]
        trap_node2.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                       if right_neighbour.content.left_segment.intersects(trapezoid2.right_segment)]

        for left_neighbour in trap_node1.left_neighbours:
            for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                if right_neighbour == node:
                    left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

        for right_neighbour in trap_node1.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node1

        for left_neighbour in trap_node2.left_neighbours:
            for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                if right_neighbour == node:
                    left_neighbour.right_neighbours[right_neighbour_index] = trap_node2

        for right_neighbour in trap_node2.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

        # Add segment endpoints to neighbour trapezoids
        for left_neighbour in node.left_neighbours:
            if left_neighbour.content.right_segment.on_segment(segment.endpoint1):
                left_neighbour.content.right_segment.append(segment.endpoint1)

        for right_neighbour in node.right_neighbours:
            if right_neighbour.content.left_segment.on_segment(segment.endpoint2):
                right_neighbour.content.left_points.append(segment.endpoint2)

    def update_multiple_trapezoids(
            self,
            nodes: [dag.DagNode],
            segment: segclass.Segment
    ) -> None:
        carry = None
        carry_complement = None

        for node in nodes:
            trapezoid = node.content

            if trapezoid.contains(segment.endpoint1):
                # Left most intersection trapezoid
                carry, carry_complement = self.update_multiple_trapezoids_left(node, trapezoid, segment)
            elif trapezoid.contains(segment.endpoint2):
                # Right most intersection trapezoid
                self.update_multiple_trapezoids_right(node, trapezoid, segment, carry, carry_complement)
            else:
                # Trapezoid is separated by segment
                carry, carry_complement = self.update_multiple_trapezoids_middle(node, trapezoid, segment, carry, carry_complement)

    def update_multiple_trapezoids_left(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment
    ) -> Tuple[None | dag.DagNode, None | dag.DagNode]:
        carry, carry_complement = None, None

        if trapezoid.right_segment.on_segment(segment.endpoint1):
            trapezoid.right_points.append(segment.endpoint1)

            # Handle case as middle or right, return for now
            return None, None
        if not trapezoid.right_segment.on_segment(segment.endpoint1):
            right_points_above_segment = [point for point in trapezoid.right_points
                                          if point.is_above(segment)]
            right_points_below_segment = [point for point in trapezoid.right_points
                                          if point.is_below(segment)]

            # 1: left of segment
            trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                             trapezoid.left_points,
                                             segment.endpoint1,
                                             trapezoid.bottom_segment)
            # 2: above segment
            trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                             segment.endpoint1,
                                             right_points_above_segment,
                                             segment)
            # 3: below segment
            trapezoid3 = trapclass.Trapezoid(segment,
                                             segment.endpoint1,
                                             right_points_below_segment,
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
            lp_node = dag.DagNode(segment.endpoint1)
            for parent_node in parent_nodes:
                if parent_node.left_child.content == trapezoid:
                    parent_node.set_left_child(lp_node)
                else:
                    parent_node.set_right_child(lp_node)

            lp_node.set_left_child(trap_node1)
            lp_node.set_right_child(dag.DagNode(segment))
            segment_node = lp_node.right_child
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
            if carry == trap_node2:
                trap_node2.right_neighbours = []
            else:
                trap_node2.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                               if right_neighbour.content.left_segment.intersects(trapezoid2.right_segment)]
                for right_neighbour in trap_node2.right_neighbours:
                    for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                        if left_neighbour == node:
                            right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

            trap_node3.left_neighbours = [trap_node1]
            if carry == trap_node3:
                trap_node3.right_neighbours = []
            else:
                trap_node3.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                               if right_neighbour.content.left_segment.intersects(trapezoid3.right_segment)]
                for right_neighbour in trap_node3.right_neighbours:
                    for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                        if left_neighbour == node:
                            right_neighbour.left_neighbours[left_neighbour_index] = trap_node3

        return carry, carry_complement

    def update_multiple_trapezoids_right(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment,
            carry: None | dag.DagNode,
            carry_complement: None | dag.DagNode
    ) -> None:
        if trapezoid.right_segment.on_segment(segment.endpoint2):
            self.update_multiple_trapezoids_right_boundary(node, trapezoid, segment, carry, carry_complement)

        if not trapezoid.right_segment.on_segment(segment.endpoint2):
            self.update_multiple_trapezoids_right_not_boundary(node, trapezoid, segment, carry, carry_complement)

    def update_multiple_trapezoids_right_boundary(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment,
            carry: None | dag.DagNode,
            carry_complement: None | dag.DagNode
    ) -> None:
        left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
        left_points_below_segment = [point for point in trapezoid.left_points if point.is_below(segment)]
        right_points_above_segment = [point for point in trapezoid.right_points if point.is_above(segment)]
        right_points_below_segment = [point for point in trapezoid.right_points if point.is_below(segment)]

        # 1: above segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         left_points_above_segment + ([segment.endpoint1]
                                                                      if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                      else []),
                                         right_points_above_segment + [segment.endpoint2],
                                         segment)
        # 2: below segment
        trapezoid2 = trapclass.Trapezoid(segment,
                                         left_points_below_segment + ([segment.endpoint1]
                                                                      if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                      else []),
                                         right_points_below_segment + [segment.endpoint2],
                                         trapezoid.bottom_segment)

        trap_node1 = dag.DagNode(trapezoid1)
        trap_node2 = dag.DagNode(trapezoid2)

        # Update neighbour lists
        if carry is not None and not left_points_above_segment:
            trap_node1.left_neighbours = carry.left_neighbours[:]
            trap_node1.content.update_left_points(carry.content.left_points)

            # Update reference to carry to refer to trap_node1
            for carry_left_neighbour in carry.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(carry_left_neighbour.right_neighbours):
                    if right_neighbour == carry:
                        carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node1
        else:
            trap_node1.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                          if left_neighbour.content.right_segment.intersects(trapezoid1.left_segment)]

            for left_neighbour in trap_node1.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

        trap_node1.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                       if right_neighbour.content.left_segment.intersects(trapezoid1.right_segment)]
        for right_neighbour in trap_node1.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node1

        if carry is not None and not left_points_below_segment:
            trap_node2.left_neighbours = carry.left_neighbours[:]
            trap_node2.content.update_left_points(carry.content.left_points)

            # Update reference to carry to refer to trap_node2
            for carry_left_neighbour in carry.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(carry_left_neighbour.right_neighbours):
                    if right_neighbour == carry:
                        carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
        else:
            trap_node2.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                          if left_neighbour.content.right_segment.intersects(trapezoid2.left_segment)]

            for left_neighbour in trap_node2.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node2

        trap_node2.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                       if right_neighbour.content.left_segment.intersects(trapezoid2.right_segment)]
        for right_neighbour in trap_node2.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

        # Add segment endpoint to neighbour trapezoids
        for right_neighbour in node.right_neighbours:
            if right_neighbour.content.left_segment.on_segment(segment.endpoint2):
                right_neighbour.content.left_points.append(segment.endpoint2)

        # Update DAG
        parent_nodes = node.parents
        lp_node = dag.DagNode(segment.endpoint2)
        for parent_node in parent_nodes:
            if parent_node.left_child == node:
                parent_node.set_left_child(lp_node)
            else:
                parent_node.set_right_child(lp_node)

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

    def update_multiple_trapezoids_right_not_boundary(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment,
            carry: None | dag.DagNode,
            carry_complement: None | dag.DagNode
    ) -> None:
        left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
        left_points_below_segment = [point for point in trapezoid.left_points if point.is_below(segment)]

        # 1: above segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         left_points_above_segment + ([segment.endpoint1]
                                                                      if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                      else []),
                                         segment.endpoint2,
                                         segment)
        # 2: below segment
        trapezoid2 = trapclass.Trapezoid(segment,
                                         left_points_below_segment + ([segment.endpoint1]
                                                                      if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                      else []),
                                         segment.endpoint2,
                                         trapezoid.bottom_segment)
        # 3: right of segment
        trapezoid3 = trapclass.Trapezoid(trapezoid.top_segment,
                                         segment.endpoint2,
                                         trapezoid.right_points,
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
                for (right_neighbour_index, right_neighbour) in enumerate(carry_left_neighbour.right_neighbours):
                    if right_neighbour == carry:
                        carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node1
        else:
            trap_node1.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                          if left_neighbour.content.right_segment.intersects(trapezoid1.left_segment)]

            for left_neighbour in trap_node1.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

        trap_node1.right_neighbours = [trap_node3]

        if carry is not None and not left_points_below_segment:
            trap_node2.left_neighbours = carry.left_neighbours[:]
            trap_node2.content.update_left_points(carry.content.left_points)

            # Update reference to carry to refer to trap_node2
            for carry_left_neighbour in carry.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(carry_left_neighbour.right_neighbours):
                    if right_neighbour == carry:
                        carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
        else:
            trap_node2.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                          if left_neighbour.content.right_segment.intersects(trapezoid2.left_segment)]

            for left_neighbour in trap_node2.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node2

        trap_node2.right_neighbours = [trap_node3]

        trap_node3.left_neighbours = [trap_node1, trap_node2]
        trap_node3.right_neighbours = node.right_neighbours[:]
        for right_neighbour in trap_node3.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node3

        # Update DAG
        parent_nodes = node.parents
        lp_node = dag.DagNode(segment.endpoint2)
        for parent_node in parent_nodes:
            if parent_node.left_child == node:
                parent_node.set_left_child(lp_node)
            else:
                parent_node.set_right_child(lp_node)

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

    def update_multiple_trapezoids_middle(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment,
            carry: None | dag.DagNode,
            carry_complement: None | dag.DagNode
    ) -> Tuple[None | dag.DagNode, None | dag.DagNode]:
        left_points_above_segment = [point for point in trapezoid.left_points if point.is_above(segment)]
        left_points_below_segment = [point for point in trapezoid.left_points if point.is_below(segment)]
        right_points_above_segment = [point for point in trapezoid.right_points if point.is_above(segment)]
        right_points_below_segment = [point for point in trapezoid.right_points if point.is_below(segment)]

        # 1: above segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         left_points_above_segment + ([segment.endpoint1]
                                                                      if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                      else []),
                                         right_points_above_segment,
                                         segment)
        # 2: below segment
        trapezoid2 = trapclass.Trapezoid(segment,
                                         left_points_below_segment + ([segment.endpoint1]
                                                                      if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                      else []),
                                         right_points_below_segment,
                                         trapezoid.bottom_segment)

        trap_node1 = dag.DagNode(trapezoid1)
        trap_node2 = dag.DagNode(trapezoid2)

        # Update left neighbour lists
        if carry is not None and not left_points_above_segment:
            trap_node1.left_neighbours = carry.left_neighbours[:]
            trap_node1.content.update_left_points(carry.content.left_points)

            # Update reference to carry to refer to trap_node1
            for carry_left_neighbour in carry.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(carry_left_neighbour.right_neighbours):
                    if right_neighbour == carry:
                        carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node1
        else:
            trap_node1.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                          if left_neighbour.content.right_segment.intersects(trapezoid1.left_segment)]
            for left_neighbour in trap_node1.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node1

        # Update left neighbour lists
        if carry is not None and not left_points_below_segment:
            trap_node2.left_neighbours = carry.left_neighbours[:]
            trap_node2.content.update_left_points(carry.content.left_points)

            # Update reference to carry to refer to trap_node2
            for carry_left_neighbour in carry.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(carry_left_neighbour.right_neighbours):
                    if right_neighbour == carry:
                        carry_left_neighbour.right_neighbours[right_neighbour_index] = trap_node2
        else:
            trap_node2.left_neighbours = [left_neighbour for left_neighbour in node.left_neighbours
                                          if left_neighbour.content.right_segment.intersects(trapezoid2.left_segment)]
            for left_neighbour in trap_node1.left_neighbours:
                for (right_neighbour_index, right_neighbour) in enumerate(left_neighbour.right_neighbours):
                    if right_neighbour == node:
                        left_neighbour.right_neighbours[right_neighbour_index] = trap_node2

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
            trap_node1.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                           if right_neighbour.content.left_segment.intersects(trapezoid1.right_segment)]
        for right_neighbour in trap_node1.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node1

        # Update right neighbour lists
        if carry == trap_node2:
            trap_node2.right_neighbours = []
        else:
            trap_node2.right_neighbours = [right_neighbour for right_neighbour in node.right_neighbours
                                           if right_neighbour.content.left_segment.intersects(trapezoid2.right_segment)]
        for right_neighbour in trap_node2.right_neighbours:
            for (left_neighbour_index, left_neighbour) in enumerate(right_neighbour.left_neighbours):
                if left_neighbour == node:
                    right_neighbour.left_neighbours[left_neighbour_index] = trap_node2

        # Update DAG
        parent_nodes = node.parents
        lp_node = dag.DagNode(segment)
        for parent_node in parent_nodes:
            if parent_node.left_child == node:
                parent_node.set_left_child(lp_node)
            else:
                parent_node.set_right_child(lp_node)

        lp_node.set_right_child(trap_node1)
        lp_node.set_left_child(trap_node2)

        return carry, carry_complement

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
            if nb not in trapl:
                return False
        for nb in node.left_neighbours:
            if nb not in trapl:
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
            b1 = node.left_child is not node.right_child
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
