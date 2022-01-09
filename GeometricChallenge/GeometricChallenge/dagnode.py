from __future__ import annotations
import typing
import vertex as vert
import segment as seg
import geometry

orientation = geometry.orientation
VERTEX = geometry.VERTEX
SEGMENT = geometry.SEGMENT
TRAPEZOID = geometry.TRAPEZOID
CW = geometry.CW
CCW = geometry.CCW


# Class that represents the DAG
class DagNode:
    # __slots__ = ('content', 'left_child', 'right_child', 'parents', 'left_neighbours', 'right_neighbours')

    def __init__(self, content) -> None:
        self.content = content
        self.left_child = None
        self.right_child = None
        self.parents = []
        self.left_neighbours = set()
        self.right_neighbours = set()

    # Choose which child is the successor for the point location search
    def choose_next_segmented(self, segment: seg.Segment, endpoint: vert.Vertex) -> 'DagNode':
        _content = self.content
        _contenttype = _content.type
        _rchild = self.right_child
        _lchild = self.left_child

        if _contenttype == TRAPEZOID:
            return self
        elif _rchild is None:
            return _lchild
        elif _lchild is None:
            return _rchild
        elif _contenttype == VERTEX:
            if endpoint.x < _content.x:
                return _lchild
            elif endpoint.x > _content.x:
                return _rchild
            else:
                # endpoint.x == self.content.x
                return _lchild if segment.endpoint2 is endpoint else _rchild
        elif _contenttype == SEGMENT:
            ori = orientation(_content.endpoint1, _content.endpoint2, endpoint)
            if ori is CW:
                return _lchild
            elif ori is CCW:
                return _rchild
            else:
                # point lies on the segment
                other_endpoint = segment.endpoint1 if endpoint is segment.endpoint2 else segment.endpoint2
                if orientation(_content.endpoint1, _content.endpoint2, other_endpoint) is CW:
                    return _lchild
                else:
                    return _rchild

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
