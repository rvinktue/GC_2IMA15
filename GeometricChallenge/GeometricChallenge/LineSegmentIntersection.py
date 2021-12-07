# Provided by the challenge
from cgshop2022utils.io import read_instance, write_instance
import networkx as nx
import random


class Trapezoid:
    def __init__(self, top_segment, left_point, right_point, bottom_segment):
        self.top_segment = top_segment
        self.left_point = left_point
        self.right_point = right_point
        self.bottom_segment = bottom_segment
        self.neighbours = []
        # Update bottom segment reference
        bottom_segment.face_above = self

    def find_intersection(self, segment):
        intersection_list = [self.bottom_segment, self.top_segment]
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

    # Calculate intersection between the two segments
    def intersects(self, segment):
        # Shared endpoint should not intersect
        if ((self.endpoint1.x == segment.endpoint1.x and self.endpoint1.y == segment.endpoint1.y) or
                (self.endpoint2.x == segment.endpoint1.x and self.endpoint2.y == segment.endpoint1.y) or
                (self.endpoint1.x == segment.endpoint2.x and self.endpoint1.y == segment.endpoint2.y) or
                (self.endpoint2.x == segment.endpoint2.x and self.endpoint2.y == segment.endpoint2.y)):
            return False

        # Find orientations
        orientation1 = orientation(self.endpoint1, self.endpoint2, segment.endpoint1)
        orientation2 = orientation(self.endpoint1, self.endpoint2, segment.endpoint2)
        orientation3 = orientation(segment.endpoint1, segment.endpoint2, self.endpoint1)
        orientation4 = orientation(segment.endpoint2, segment.endpoint2, self.endpoint2)

        # Endpoint of one line situated on other line should not intersect
        if ((orientation1 == 0 and on_segment(self.endpoint1, segment.endpoint1, self.endpoint2)) or
                (orientation2 == 0 and on_segment(self.endpoint1, segment.endpoint2, self.endpoint2)) or
                (orientation3 == 0 and on_segment(segment.endpoint1, self.endpoint1, segment.endpoint2)) or
                (orientation4 == 0 and on_segment(segment.endpoint1, self.endpoint2, segment.endpoint2))):
            return False

        # Different orientations means lines intersect
        if (orientation1 != orientation2) and (orientation3 != orientation4):
            return True

        # All other cases do not intersect
        return False

    def orientation_test(self, point):
        return orientation(self.endpoint1, self.endpoint2, point)


class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Returns 0 if they share their x-coordinate
    #         1 if this vertex lies to the left of point
    #         -1 if this vertex lies to the right of point
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

    # Choose which child is the successor for the point location search
    def choose_next(self, point):
        if isinstance(self.content, Trapezoid):
            return self
        elif isinstance(self.content, Vertex):
            return self.left_child if self.content.orientation(point) == -1 else self.right_child
        else:
            return self.left_child if self.content.orientation_test(point) == 1 else self.right_child

    # Add segment


# Class that represent the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        self.dag = DagNode(bounding_box, None, None)

    # Finds and returns the trapezoid in which the requested point lies
    def find_point_location(self, point):
        current_node = self.dag
        while not isinstance(current_node.content, Trapezoid):
            current_node = current_node.choose_next(point)
        return current_node

    # Finds all trapezoids that intersect the segment
    def find_intersecting_faces(self, segment):
        # todo: implement method to find all faces intersected by segment
        assert(False, "VD: Find intersecting faces not implemented yet")
        return []

    # Adds a new segment to the vertical decomposition if it does not intersect
    # Returns True if segment could be inserted in this vertical decomposition
    #         False if segment could not be inserted in this vertical decomposition
    def add_segment(self, segment):
        intersecting_faces = self.find_intersecting_faces(segment)
        for face in intersecting_faces:
            # Checks if the segment has an intersection with the boundary of the face
            if face.find_intersection(segment):
                return False

        # todo: insert segment into dag (recompute vertical decomposition)
        return True


# Incrementally build vertical decompositions of planar subgraphs
def main():
    # Read instance and instantiate graph, bounding box and starting vertical decomposition
    instance = read_instance('insert_file_name_here')  # read edges from input file
    g = instance["graph"]

    edges = g.edges
    random.shuffle(edges)  # Find random reordering of edges to decrease expected running time complexity

    bounding_box = find_bounding_box(g.nodes)
    vds = [VerticalDecomposition(bounding_box)]

    # Process all edges
    for edge in edges:
        for (key, vd) in vds:
            if vd.add_segment(edge):
                # If segment can be added to the vertical decomposition of level key: add it and continue to next edge
                continue
            elif key == len(vds):
                # If segment could not be added in any of the existing VDs, create a new VD
                new = VerticalDecomposition(bounding_box)
                new.add_segment(edge)
                vds.append(new)

    # Return an upperbound on the edge-colouring
    return len(vds)


# Returns a bounding box for the set of nodes as a trapezoid
def find_bounding_box(nodes):
    min_x = min_y = max_x = max_y = 0
    for node in nodes:
        min_x, min_y, max_x, max_y = min(node[0], min_x), min(node[1], min_y), max(node[0], max_x), max(node[1], max_y)

    # Build the trapezoid of the bounding box
    # todo: even nadenken of het nodig is om ruimte te hebben tussen de bounding box en de nodes (if so, dan `max = max + 1` en `min = min - 1` pakken)
    left_top = Vertex(min_x, max_y)
    right_top = Vertex(max_x, max_y)
    left_bottom = Vertex(min_x, min_y)
    right_bottom = Vertex(max_x, min_y)

    return Trapezoid(Segment(left_top, right_top, None), left_bottom, right_top, Segment(left_bottom, right_bottom, None))


def add_intersection_to_output(intersection_list):
    # todo: waardes wegschrijven naar output file implementeren
    assert(False, "Main: adding intersection to output not implemented yet")
    return None


# Returns 0 if the three points are collinear,
#         1 if traversing the points in order of arguments given makes a right turn (clockwise)
#         2 if traversing the points in order of arguments given makes a left turn (counterclockwise)
def orientation(point1, point2, point3):
    val = (float(point2.y - point1.y) * (point3.x - point2.x)) - (float(point2.x - point1.x) * (point3.y - point2.y))
    if val > 0:
        return 1  # Clockwise
    elif val < 0:
        return 2  # Counterclockwise
    else:
        return 0  # Collinear


# Checks if point2 is contained on the line segment with endpoints point1 and point3
# where we assume the three points are collinear
def on_segment(point1, point2, point3):
    if ((point2.x <= max(point1.x, point3.x)) and (point2.x >= min(point1.x, point3.x)) and
            (point2.y <= max(point1.y, point3.y)) and (point2.y >= min(point1.y, point3.y))):
        return True
    return False


##### TESTING #####
print("hello")
test = Vertex(1, 2)
test3 = Vertex(2, 3)
test2 = Segment(test, test3, None)
print(DagNode(test2, None, None))
