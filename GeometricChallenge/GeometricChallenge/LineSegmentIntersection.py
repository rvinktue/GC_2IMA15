# Provided by the challenge
from cgshop2022utils.io import read_instance, write_instance
import networkx as nx
import random


class Trapezoid:
    def __init__(self, top, leftp, rightp, bottom):
        self.top = top
        self.leftp = leftp
        self.rightp = rightp
        self.bottom = bottom
        self.neighbours = []
        # update bottom reference
        bottom.face_above = self

    def find_intersection(self, segment):
        # insert smart way to find intersection of segment with face
        intersection_list = [self.bottom, self.top]
        intersection_list = [line for line in intersection_list if line.intersects(segment)]

        if len(intersection_list) > 0:
            add_intersection_to_output(intersection_list)
            return True

        return False


class Segment:
    def __init__(self, endpoint1, endpoint2, face_above):
        self.endpoint1 = endpoint1 if endpoint1.x <= endpoint2.x else endpoint2
        self.endpoint2 = endpoint2 if endpoint1.x <= endpoint2.x else endpoint1
        self.face_above = face_above

    def intersects(self, segment):
        # Calculate intersection between the two segments
        orientation1 = orientation(self.endpoint1, segment.endpoint1, self.endpoint2)
        orientation2 = orientation(self.endpoint1, segment.endpoint1, segment.endpoint2)
        orientation3 = orientation(self.endpoint2, segment.endpoint2, self.endpoint1)
        orientation4 = orientation(self.endpoint2, segment.endpoint2, segment.endpoint1)

        if (((orientation1 != orientation2) and (orientation3 != orientation4)) or
                ((orientation1 == 0) and on_segment(self.endpoint1, self.endpoint2, segment.endpoint1)) or
                ((orientation2 == 0) and on_segment(self.endpoint1, segment.endpoint2, segment.endpoint1)) or
                ((orientation3 == 0) and on_segment(segment.endpoint1, self.endpoint1, segment.endpoint2)) or
                ((orientation4 == 0) and on_segment(segment.endpoint1, segment.endpoint1, segment.endpoint2))):
            return True

        return False

    def orientation_test(self, point):
        return orientation(self.endpoint1, self.endpoint2, point)


class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # returns 0 if they lie the same horizontally, 1 if this lies to the left, -1 if this lies to the right
    def orientation(self, point):
        if self.x == point.x:
            return 0
        else:
            return 1 if point.x > self.x else -1


class DagNode:
    def __init__(self, content, left_child, right_child):
        self.content = content
        self.left_child = left_child
        self.right_child = right_child

    # chooses which child to go to next for the point location search
    def choose_next(self, point):
        if isinstance(self.content, Trapezoid):
            return self
        elif isinstance(self.content, Vertex):
            return self.left_child if self.content.orientation(point) == -1 else self.right_child
        else:
            return self.left_child if self.content.orientation_test(point) == 1 else self.right_child


# Class that represent the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        # see https://mungingdata.com/python/dag-directed-acyclic-graph-networkx/
        # self.dag = nx.DiGraph()  # initialize an empty dag
        # self.dag.add_node(1, content=boundingBox)
        self.dag = DagNode(bounding_box, None, None)

    # finds and returns the trapezoid in which the point lies
    def find_point_location(self, point):
        current_node = self.dag
        while not isinstance(current_node.content, Trapezoid):
            current_node = current_node.choose_next(point)
        return current_node

    # Finds all trapezoids that intersect the segment
    def find_intersecting_faces(self, segment):
        assert(False, "VD: Find intersecting faces not implemented yet")
        return []

    # adds a new segment to the vertical decomposition
    def add_segment(self, segment):
        intersecting_faces = self.find_intersecting_faces(segment)
        for face in intersecting_faces:
            # Checks if the segment has an intersection with the boundary of the face
            if face.find_intersection(segment):
                return False

        return True


# Incrementally build vertical decompositions of planar subgraphs
def main():
    instance = read_instance('insert_file_name_here')  # read edges from input file
    g = instance["graph"]
    edges = g.edges
    random.shuffle(edges)  # find random reordering of edges
    bounding_box = find_bounding_box(g.nodes)

    vds = [VerticalDecomposition(bounding_box)]  # init first VD

    for edge in edges:
        for (key, vd) in vds:
            if vd.add_segment(edge):
                # if segment can be added to VD of level key, add it and continue to next edge
                continue
            elif key == len(vds):
                # if segment could not be added in any of the existing VDs, create a new VD
                new = VerticalDecomposition(bounding_box)
                new.add_segment(edge)
                vds.append(new)

    return len(vds)


# Returns a bounding box for the set of nodes as a trapezoid
def find_bounding_box(nodes):
    minx = miny = maxx = maxy = 0
    for node in nodes:
        minx, miny, maxx, maxy = min(node[0], minx), min(node[1], miny), max(node[0], maxx), max(node[1], maxy)
    # build the trapezoid of the bounding box
    lt = Vertex(minx, maxy)
    rt = Vertex(maxx, maxy)
    lb = Vertex(minx, miny)
    rb = Vertex(maxx, miny)

    return Trapezoid(Segment(lt, rt, None), lb, rt, Segment(lb, rb, None))


def add_intersection_to_output(intersection_list):
    assert(False, "Main: adding intersection to output not implemented yet")
    return None


def orientation(point1, point2, point3):
    val = (float(point2.y - point1.y) * (point3.x - point2.x)) - (float(point2.x - point1.x) * (point3.y - point2.y))
    if val > 0:
        return 1  # Clockwise
    elif val < 0:
        return 2  # Counterclockwise
    else:
        return 0  # Collinear


def on_segment(point1, point2, point3):
    if ((point2.x <= max(point1.x, point3.x)) and (point2.x >= min(point1.x, point3.x)) and
            (point2.y <= max(point1.y, point3.y)) and (point2.y >= min(point1.y, point3.y))):
        return True
    return False


print("hello")
dag = nx.DiGraph()  # initialize an empty dag
test = Vertex(1, 2)
test3 = Vertex(2, 3)
test2 = Segment(test, test3, None)
dag.add_node(1, content=test)
dag.add_node(2, content=test2)
print(dag.nodes[1])
print(dag.nodes[2])
print(DagNode(test2, None, None))
