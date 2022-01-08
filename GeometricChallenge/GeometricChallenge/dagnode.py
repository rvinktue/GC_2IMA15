from __future__ import annotations
import typing
import trapezoid as trap
import vertex as vert
import segment as seg
import geometry


# Class that represents the DAG
class DagNode:
    def __init__(self, content, left_child=None, right_child=None, parents=None) -> None:
        self.content = content
        self.left_child = left_child
        self.right_child = right_child
        self.parents = parents
        if parents is None:
            self.parents = []
        self.left_neighbours = set()
        self.right_neighbours = set()

    # Choose which child is the successor for the point location search
    def choose_next_segmented(self, segment: seg.Segment, endpoint: vert.Vertex) -> 'DagNode':
        if isinstance(self.content, trap.Trapezoid):
            return self
        elif self.right_child is None:
            return self.left_child
        elif self.left_child is None:
            return self.right_child
        elif isinstance(self.content, vert.Vertex):
            if endpoint.x < self.content.x:
                return self.left_child
            elif endpoint.x > self.content.x:
                return self.right_child
            else:
                # endpoint.x == self.content.x
                return self.left_child if segment.endpoint2 is endpoint else self.right_child
        elif isinstance(self.content, seg.Segment):
            ori = geometry.orientation(self.content.endpoint1, self.content.endpoint2, endpoint)
            if ori is geometry.CW:
                return self.left_child
            elif ori is geometry.CCW:
                return self.right_child
            else:
                # point lies on the segment
                other_endpoint = segment.endpoint1 if endpoint is segment.endpoint2 else segment.endpoint2
                if geometry.orientation(self.content.endpoint1, self.content.endpoint2, other_endpoint) is geometry.CW:
                    return self.left_child
                else:
                    return self.right_child

    # @TODO: this is a debug method: delete upon release
    # Find all objects of class
    def find_all(self, object_class) -> typing.Set[object]:
        output = set()
        if isinstance(self.content, object_class):
            output.add(self)
        if self.left_child is not None:
            output.update(self.left_child.find_all(object_class))
        if self.right_child is not None:
            output.update(self.right_child.find_all(object_class))
        return output

    # Set left child
    def set_left_child(self, other: 'DagNode') -> None:
        self.left_child = other
        other.parents.append(self)

    # Set right child
    def set_right_child(self, other: 'DagNode') -> None:
        self.right_child = other
        other.parents.append(self)
