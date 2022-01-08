from __future__ import annotations
from typing import Tuple
import dagnode as dag
import trapezoid as trapclass
import segment as segclass
import test_draw
import matplotlib.pyplot as plt


# Class that represents the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        self.dag = dag.DagNode(bounding_box)

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

        if not start_node.content.is_valid(segment.endpoint1) or not end_node.content.is_valid(segment.endpoint2):
            return []

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
            update_multiple_trapezoids(nodes, segment)

    def update_single_trapezoid(self, nodes: [dag.DagNode], segment: segclass.Segment) -> None:
        # Segment is completely contained in a single trapezoid
        node = nodes[0]
        trapezoid = node.content

        if not trapezoid.left_segment.on_segment(segment.endpoint1) \
                and not trapezoid.right_segment.on_segment(segment.endpoint2):
            self.update_single_trapezoid_contained(node, trapezoid, segment)

        if trapezoid.left_segment.on_segment(segment.endpoint1) \
                and not trapezoid.right_segment.on_segment(segment.endpoint2):
            update_single_trapezoid_left_boundary(node, trapezoid, segment)

        if not trapezoid.left_segment.on_segment(segment.endpoint1) \
                and trapezoid.right_segment.on_segment(segment.endpoint2):
            update_single_trapezoid_right_boundary(node, trapezoid, segment)

        if trapezoid.left_segment.on_segment(segment.endpoint1) \
                and trapezoid.right_segment.on_segment(segment.endpoint2):
            update_single_trapezoid_both_boundary(node, trapezoid, segment)

    def update_single_trapezoid_contained(
            self,
            node: dag.DagNode,
            trapezoid: trapclass.Trapezoid,
            segment: segclass.Segment
    ) -> None:
        # 1: left of segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         trapezoid.left_points,
                                         [segment.endpoint1],
                                         trapezoid.bottom_segment)
        # 2: above segment
        trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                         [segment.endpoint1],
                                         [segment.endpoint2],
                                         segment)
        # 3: below segment
        trapezoid3 = trapclass.Trapezoid(segment,
                                         [segment.endpoint1],
                                         [segment.endpoint2],
                                         trapezoid.bottom_segment)
        # 4: right of segment
        trapezoid4 = trapclass.Trapezoid(trapezoid.top_segment,
                                         [segment.endpoint2],
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
                if parent_node.left_child == node:  # If we are the left child
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
        # External neighbours
        for left_neighbour in node.left_neighbours:
            left_neighbour.right_neighbours.discard(node)
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)
        for right_neighbour in node.right_neighbours:
            right_neighbour.left_neighbours.discard(node)
            right_neighbour.left_neighbours.add(trap_node4)
            trap_node4.right_neighbours.add(right_neighbour)

        # Internal neighbours
        trap_node1.right_neighbours = {trap_node2, trap_node3}
        trap_node2.left_neighbours = {trap_node1}
        trap_node2.right_neighbours = {trap_node4}
        trap_node3.left_neighbours = {trap_node1}
        trap_node3.right_neighbours = {trap_node4}
        trap_node4.left_neighbours = {trap_node2, trap_node3}


def update_single_trapezoid_left_boundary(
        node: dag.DagNode,
        trapezoid: trapclass.Trapezoid,
        segment: segclass.Segment
) -> None:
    left_points_above_segment = [point for point in trapezoid.left_points
                                 if point.is_above(segment)]
    left_points_below_segment = [point for point in trapezoid.left_points
                                 if point.is_below(segment)]

    # 1: above segment
    trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                     left_points_above_segment + [segment.endpoint1],
                                     [segment.endpoint2],
                                     segment)
    # 2: below segment
    trapezoid2 = trapclass.Trapezoid(segment,
                                     left_points_below_segment + [segment.endpoint1],
                                     [segment.endpoint2],
                                     trapezoid.bottom_segment)

    # 3: right of segment
    trapezoid3 = trapclass.Trapezoid(trapezoid.top_segment,
                                     [segment.endpoint2],
                                     trapezoid.right_points,
                                     trapezoid.bottom_segment)

    trap_node1 = dag.DagNode(trapezoid1)
    trap_node2 = dag.DagNode(trapezoid2)
    trap_node3 = dag.DagNode(trapezoid3)

    # Update DAG
    parent_nodes = node.parents
    lp_node = dag.DagNode(segment.endpoint1)
    for parent_node in parent_nodes:
        if parent_node.left_child == node:  # If we are the left child
            parent_node.set_left_child(lp_node)  # Left endpoint becomes left child
        else:
            # We are the right child
            parent_node.set_right_child(lp_node)  # Left endpoint becomes right child

    lp_node.set_right_child(dag.DagNode(segment.endpoint2))
    lp_node.right_child.set_right_child(trap_node3)
    lp_node.right_child.set_left_child(dag.DagNode(segment))
    segment_node = lp_node.right_child.left_child
    segment_node.set_left_child(trap_node2)
    segment_node.set_right_child(trap_node1)

    # Update neighbours
    # External neighbours
    for left_neighbour in node.left_neighbours:
        left_neighbour.right_neighbours.discard(node)
        if trapezoid1.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)
        if trapezoid2.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node2)
            trap_node2.left_neighbours.add(left_neighbour)
    for right_neighbour in node.right_neighbours:
        right_neighbour.left_neighbours.discard(node)
        right_neighbour.left_neighbours.add(trap_node3)
        trap_node3.right_neighbours.add(right_neighbour)

    # Internal neighbours
    trap_node1.right_neighbours = {trap_node3}
    trap_node2.right_neighbours = {trap_node3}
    trap_node3.left_neighbours = {trap_node1, trap_node2}

    # Add segment endpoint to neighbour trapezoids
    for left_neighbour in node.left_neighbours:
        if left_neighbour.content.right_segment.on_segment(segment.endpoint1):
            left_neighbour.content.right_points.append(segment.endpoint1)


def update_single_trapezoid_right_boundary(
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
                                     [segment.endpoint1],
                                     trapezoid.bottom_segment)
    # 2: above segment
    trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                     [segment.endpoint1],
                                     right_points_above_segment + [segment.endpoint2],
                                     segment)

    # 3: below segment
    trapezoid3 = trapclass.Trapezoid(segment,
                                     [segment.endpoint1],
                                     right_points_below_segment + [segment.endpoint2],
                                     trapezoid.bottom_segment)

    trap_node1 = dag.DagNode(trapezoid1)
    trap_node2 = dag.DagNode(trapezoid2)
    trap_node3 = dag.DagNode(trapezoid3)

    # Update DAG
    parent_nodes = node.parents
    lp_node = dag.DagNode(segment.endpoint1)
    for parent_node in parent_nodes:
        if parent_node.left_child == node:  # If we are the left child
            parent_node.set_left_child(lp_node)  # Left endpoint becomes left child
        else:
            # We are the right child
            parent_node.set_right_child(lp_node)  # Left endpoint becomes right child

    lp_node.set_left_child(trap_node1)
    lp_node.set_right_child(dag.DagNode(segment.endpoint2))
    lp_node.right_child.set_left_child(dag.DagNode(segment))
    segment_node = lp_node.right_child.left_child
    segment_node.set_left_child(trap_node3)
    segment_node.set_right_child(trap_node2)

    # Update neighbours
    # External neighbours
    for left_neighbour in node.left_neighbours:
        left_neighbour.right_neighbours.discard(node)
        left_neighbour.right_neighbours.add(trap_node1)
        trap_node1.left_neighbours.add(left_neighbour)
    for right_neighbour in node.right_neighbours:
        right_neighbour.left_neighbours.discard(node)
        if trapezoid2.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node2)
            trap_node2.right_neighbours.add(right_neighbour)
        if trapezoid3.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node3)
            trap_node3.right_neighbours.add(right_neighbour)

    # Internal neighbours
    trap_node1.right_neighbours = {trap_node2, trap_node3}
    trap_node2.left_neighbours = {trap_node1}
    trap_node3.left_neighbours = {trap_node1}

    # Add segment endpoint to neighbour trapezoids
    for right_neighbour in node.right_neighbours:
        if right_neighbour.content.left_segment.on_segment(segment.endpoint2):
            right_neighbour.content.left_points.append(segment.endpoint2)


def update_single_trapezoid_both_boundary(
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
        if parent_node.left_child == node:  # If we are the left child
            parent_node.set_left_child(lp_node)  # Left endpoint becomes left child
        else:
            # We are the right child
            parent_node.set_right_child(lp_node)  # Left endpoint becomes right child

    lp_node.set_right_child(dag.DagNode(segment.endpoint2))
    lp_node.right_child.set_left_child(dag.DagNode(segment))
    segment_node = lp_node.right_child.left_child
    segment_node.set_left_child(trap_node2)
    segment_node.set_right_child(trap_node1)

    # Update neighbours
    # External neighbours
    for left_neighbour in node.left_neighbours:
        left_neighbour.right_neighbours.discard(node)
        if trapezoid1.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)
        if trapezoid2.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node2)
            trap_node2.left_neighbours.add(left_neighbour)
    for right_neighbour in node.right_neighbours:
        right_neighbour.left_neighbours.discard(node)
        if trapezoid1.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node1)
            trap_node1.right_neighbours.add(right_neighbour)
        if trapezoid2.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node2)
            trap_node2.right_neighbours.add(right_neighbour)

    # No internal neighbours

    # Add segment endpoints to neighbour trapezoids
    for left_neighbour in node.left_neighbours:
        if left_neighbour.content.right_segment.on_segment(segment.endpoint1):
            left_neighbour.content.right_points.append(segment.endpoint1)

    for right_neighbour in node.right_neighbours:
        if right_neighbour.content.left_segment.on_segment(segment.endpoint2):
            right_neighbour.content.left_points.append(segment.endpoint2)


def update_multiple_trapezoids(
        nodes: [dag.DagNode],
        segment: segclass.Segment
) -> None:
    carry = None
    carry_complement = None

    for node in nodes:
        trapezoid = node.content

        if trapezoid.contains(segment.endpoint1):
            # Left most intersection trapezoid
            carry, carry_complement = update_multiple_trapezoids_left(node, trapezoid, segment)
        elif trapezoid.contains(segment.endpoint2):
            # Right most intersection trapezoid
            update_multiple_trapezoids_right(node, trapezoid, segment, carry, carry_complement)
        else:
            # Trapezoid is separated by segment
            carry, carry_complement = update_multiple_trapezoids_middle(node, trapezoid, segment, carry, carry_complement)


def update_multiple_trapezoids_left(
        node: dag.DagNode,
        trapezoid: trapclass.Trapezoid,
        segment: segclass.Segment
) -> Tuple[None | dag.DagNode, None | dag.DagNode]:
    carry, carry_complement = None, None

    if trapezoid.right_segment.on_segment(segment.endpoint1):
        trapezoid.right_points.append(segment.endpoint1)

        # Handle case as middle or right, return for now
        return None, None
    elif trapezoid.left_segment.on_segment(segment.endpoint1):
        trapezoid.left_points.append(segment.endpoint1)

        # Handle case as middle with left endpoint on left boundary
        return update_multiple_trapezoids_middle(node, trapezoid, segment, carry, carry_complement)
    else:
        right_points_above_segment = [point for point in trapezoid.right_points
                                      if point.is_above(segment)]
        right_points_below_segment = [point for point in trapezoid.right_points
                                      if point.is_below(segment)]

        # 1: left of segment
        trapezoid1 = trapclass.Trapezoid(trapezoid.top_segment,
                                         trapezoid.left_points,
                                         [segment.endpoint1],
                                         trapezoid.bottom_segment)
        # 2: above segment
        trapezoid2 = trapclass.Trapezoid(trapezoid.top_segment,
                                         [segment.endpoint1],
                                         right_points_above_segment,
                                         segment)
        # 3: below segment
        trapezoid3 = trapclass.Trapezoid(segment,
                                         [segment.endpoint1],
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
            if parent_node.left_child == node:
                parent_node.set_left_child(lp_node)
            else:
                parent_node.set_right_child(lp_node)

        lp_node.set_left_child(trap_node1)
        lp_node.set_right_child(dag.DagNode(segment))
        segment_node = lp_node.right_child
        segment_node.set_left_child(trap_node3)
        segment_node.set_right_child(trap_node2)

        # Update neighbour lists
        # External neighbours
        for left_neighbour in node.left_neighbours:
            left_neighbour.right_neighbours.discard(node)
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)
        for right_neighbour in node.right_neighbours:
            right_neighbour.left_neighbours.discard(node)
            if carry is not trap_node2 \
                    and trapezoid2.right_segment.intersects_vertical(right_neighbour.content.left_segment):
                right_neighbour.left_neighbours.add(trap_node2)
                trap_node2.right_neighbours.add(right_neighbour)
            if carry is not trap_node3 \
                    and trapezoid3.right_segment.intersects_vertical(right_neighbour.content.left_segment):
                right_neighbour.left_neighbours.add(trap_node3)
                trap_node3.right_neighbours.add(right_neighbour)

        # Internal neighbours
        trap_node1.right_neighbours = {trap_node2, trap_node3}
        trap_node2.left_neighbours = {trap_node1}
        trap_node3.left_neighbours = {trap_node1}

    return carry, carry_complement


def update_multiple_trapezoids_right(
        node: dag.DagNode,
        trapezoid: trapclass.Trapezoid,
        segment: segclass.Segment,
        carry: None | dag.DagNode,
        carry_complement: None | dag.DagNode
) -> None:
    if trapezoid.right_segment.on_segment(segment.endpoint2):
        update_multiple_trapezoids_right_boundary(node, trapezoid, segment, carry, carry_complement)

    if not trapezoid.right_segment.on_segment(segment.endpoint2):
        update_multiple_trapezoids_right_not_boundary(node, trapezoid, segment, carry, carry_complement)


def update_multiple_trapezoids_right_boundary(
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
    # External neighbours
    for left_neighbour in node.left_neighbours:
        left_neighbour.right_neighbours.discard(node)

        # Carry should be merged with trapezoid1
        if left_points_above_segment \
                and trapezoid1.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)

        # Carry should be merged with trapezoid1
        if left_points_below_segment \
                and trapezoid2.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node2)
            trap_node2.left_neighbours.add(left_neighbour)
    for right_neighbour in node.right_neighbours:
        right_neighbour.left_neighbours.discard(node)
        if trapezoid1.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node1)
            trap_node1.right_neighbours.add(right_neighbour)
        if trapezoid2.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node2)
            trap_node2.right_neighbours.add(right_neighbour)

    # No internal neighbours

    # Merge carry
    if carry is not None:
        if not left_points_above_segment:  # Carry should be merged with trapezoid1
            trapezoid1.update_left_points(carry.content.left_points)
            for left_neighbour in carry.left_neighbours:
                left_neighbour.right_neighbours.discard(carry)
                left_neighbour.right_neighbours.add(trap_node1)
                trap_node1.left_neighbours.add(left_neighbour)
        if not left_points_below_segment:  # Carry should be merged with trapezoid2
            trapezoid2.update_left_points(carry.content.left_points)
            for left_neighbour in carry.left_neighbours:
                left_neighbour.right_neighbours.discard(carry)
                left_neighbour.right_neighbours.add(trap_node2)
                trap_node2.left_neighbours.add(left_neighbour)

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
                                     [segment.endpoint2],
                                     segment)
    # 2: below segment
    trapezoid2 = trapclass.Trapezoid(segment,
                                     left_points_below_segment + ([segment.endpoint1]
                                                                  if trapezoid.left_segment.on_segment(segment.endpoint1)
                                                                  else []),
                                     [segment.endpoint2],
                                     trapezoid.bottom_segment)
    # 3: right of segment
    trapezoid3 = trapclass.Trapezoid(trapezoid.top_segment,
                                     [segment.endpoint2],
                                     trapezoid.right_points,
                                     trapezoid.bottom_segment)

    trap_node1 = dag.DagNode(trapezoid1)
    trap_node2 = dag.DagNode(trapezoid2)
    trap_node3 = dag.DagNode(trapezoid3)

    # Update neighbour lists
    # External neighbours
    for left_neighbour in node.left_neighbours:
        left_neighbour.right_neighbours.discard(node)

        # Carry should be merged with trapezoid1
        if left_points_above_segment \
                and trapezoid1.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)

        # Carry should be merged with trapezoid2
        if left_points_below_segment \
                and trapezoid2.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node2)
            trap_node2.left_neighbours.add(left_neighbour)
    for right_neighbour in node.right_neighbours:
        right_neighbour.left_neighbours.discard(node)
        right_neighbour.left_neighbours.add(trap_node3)
        trap_node3.right_neighbours.add(right_neighbour)

    # Internal neighbours
    trap_node1.right_neighbours = {trap_node3}
    trap_node2.right_neighbours = {trap_node3}
    trap_node3.left_neighbours = {trap_node1, trap_node2}

    # Merge carry
    if carry is not None:
        if not left_points_above_segment:  # Carry should be merged with trapezoid1
            trapezoid1.update_left_points(carry.content.left_points)
            for left_neighbour in carry.left_neighbours:
                left_neighbour.right_neighbours.discard(carry)
                left_neighbour.right_neighbours.add(trap_node1)
                trap_node1.left_neighbours.add(left_neighbour)
        if not left_points_below_segment:  # Carry should be merged with trapezoid2
            trapezoid2.update_left_points(carry.content.left_points)
            for left_neighbour in carry.left_neighbours:
                left_neighbour.right_neighbours.discard(carry)
                left_neighbour.right_neighbours.add(trap_node2)
                trap_node2.left_neighbours.add(left_neighbour)

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

        try:
            for parent in carry.parents:
                if parent.left_child == carry:
                    parent.set_left_child(carry_complement)
                else:
                    parent.set_right_child(carry_complement)
        except Exception as e:
            dags = None
            while len(node.parents) > 0:
                dags = node.parents[0]
                node = node.parents[0]
            test_draw.test_draw_dag(dags)
            test_draw.test_draw_segment(segment, color=(1, 0, 1))
            plt.show()


def update_multiple_trapezoids_middle(
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
    # External neighbours
    for left_neighbour in node.left_neighbours:
        left_neighbour.right_neighbours.discard(node)

        # Carry should be merged with trapezoid1
        if left_points_above_segment \
                and trapezoid1.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node1)
            trap_node1.left_neighbours.add(left_neighbour)

        # Carry should be merged with trapezoid2
        if left_points_below_segment \
                and trapezoid2.left_segment.intersects_vertical(left_neighbour.content.right_segment):
            left_neighbour.right_neighbours.add(trap_node2)
            trap_node2.left_neighbours.add(left_neighbour)

    # No internal neighbours

    # Merge carry
    if carry is not None:
        if not left_points_above_segment:  # Carry should be merged with trapezoid1
            trapezoid1.update_left_points(carry.content.left_points)
            for left_neighbour in carry.left_neighbours:
                left_neighbour.right_neighbours.discard(carry)
                left_neighbour.right_neighbours.add(trap_node1)
                trap_node1.left_neighbours.add(left_neighbour)
        if not left_points_below_segment:  # Carry should be merged with trapezoid2
            trapezoid2.update_left_points(carry.content.left_points)
            for left_neighbour in carry.left_neighbours:
                left_neighbour.right_neighbours.discard(carry)
                left_neighbour.right_neighbours.add(trap_node2)
                trap_node2.left_neighbours.add(left_neighbour)

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
    for right_neighbour in node.right_neighbours:
        right_neighbour.left_neighbours.discard(node)
        if carry is not trap_node1 \
                and trapezoid1.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node1)
            trap_node1.right_neighbours.add(right_neighbour)
        if carry is not trap_node2 \
                and trapezoid2.right_segment.intersects_vertical(right_neighbour.content.left_segment):
            right_neighbour.left_neighbours.add(trap_node2)
            trap_node2.right_neighbours.add(right_neighbour)

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
