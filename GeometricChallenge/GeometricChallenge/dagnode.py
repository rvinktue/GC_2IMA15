import trapezoid as trap
import vertex as vert
import segment as seg
import geometry


# Class that represents the DAG
class DagNode:
    def __init__(self, content, left_child=None, right_child=None, parents=None):
        self.content = content
        self.left_child = left_child
        self.right_child = right_child
        self.parents = parents
        if parents is None:
            self.parents = []
        self.left_neighbours = []
        self.right_neighbours = []

    # Choose which child is the successor for the point location search
    def choose_next(self, point):
        if isinstance(self.content, trap.Trapezoid):
            return self
        elif isinstance(self.content, vert.Vertex):
            return self.left_child if self.content.x_order(point) == -1 else self.right_child
        elif isinstance(self.content, seg.Segment):
            return self.left_child if \
                geometry.orientation(self.content.endpoint1, self.content.endpoint2, point) == geometry.CW \
                else self.right_child
        else:
            assert False, "DagNode: Encountered content of unexpected instance %s" % type(self.content).__name__

    # Choose which child is the successor for the point location search
    def choose_next_segmented(self, segment, endpoint):
        if isinstance(self.content, trap.Trapezoid):
            return self
        elif isinstance(self.content, vert.Vertex):
            if endpoint.x < self.content.x:
                return self.left_child
            elif endpoint.x > self.content.x:
                return self.right_child
            else:
                #endpoint.x == self.content.x
                return self.left_child if segment.endpoint2 is endpoint else self.right_child
        elif isinstance(self.content, seg.Segment):
            ori = geometry.orientation(self.content.endpoint1, self.content.endpoint2, endpoint)
            if ori is geometry.CW:
                return self.left_child
            elif ori is geometry.CCW:
                return self.right_child
            else:
                #point lies on the segment
                other_endpoint = segment.endpoint1 if endpoint is segment.endpoint2 else segment.endpoint2
                if geometry.orientation(self.content.endpoint1, self.content.endpoint2, other_endpoint) is geometry.CW:
                    return self.left_child
                else:
                    return self.right_child

        else:
            assert False, "DagNode: Encountered content of unexpected instance %s" % type(self.content).__name__


    # Find all objects of class
    def find_all(self, object_class):
        output = []
        if isinstance(self.content, object_class):
            output.append(self)
        if self.left_child is not None:
            output += self.left_child.find_all(object_class)
        if self.right_child is not None:
            output += self.right_child.find_all(object_class)
        return output

    # Find all references to node
    def find_all_node(self, node):
        output = []
        if self.content == node.content:
            output.append(self)
        if self.left_child is not None:
            output += self.left_child.find_all_node(node)
        if self.right_child is not None:
            output += self.right_child.find_all_node(node)
        return output

    def reset_parent(self):
        self.parents = []

    # Set left child
    def set_left_child(self, other):
        assert isinstance(other, DagNode), "Expected other to be of type DagNode, found: %s" % type(other).__name__
        self.left_child = other
        other.parents.append(self)

    # Set right child
    def set_right_child(self, other):
        assert isinstance(other, DagNode), "Expected other to be of type DagNode, found: %s" % type(other).__name__
        self.right_child = other
        other.parents.append(self)
