from cgshop2022utils.io import read_instance, write_instance  # Provided by the challenge
import random

INPUT_FILE = "input_file_name"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file


# Class that represents a single Trapezoid in the Vertical Decomposition
class Trapezoid:
    def __init__(self, top_segment, left_points, right_points, bottom_segment):
        self.top_segment = top_segment
        self.left_points = left_points
        self.right_points = right_points
        self.bottom_segment = bottom_segment
        self.neighbours = []
        # Update bottom segment reference
        bottom_segment.face_above = self

    def find_intersection(self, segment):
        # Only compare with bottom segment. If it also intersects top segment,
        # then the intersection will be added when we evaluate the corresponding
        # trapezoid as segment will also intersect that trapezoid.
        if self.bottom_segment.intersects(segment) > 0:
            add_intersection_to_output(self.bottom_segment, segment)
            return True

        return False

    # Returns true if the segment crosses this trapezoid
    def intersects_segment(self, segment):
        #left lies above right
        return orientation(segment.endpoint1, segment.endpoint2, self.bottom_segment.endpoint1) == 1 and orientation(segment.endpoint1, segment.endpoint2, self.top_segment.endpoint1) == 2



# Class that represents a single line segment between two vertices
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

        # Segments should intersect if they overlap
        if ((orientation1 == 0 and orientation2 == 0 and orientation3 == 0 and orientation4 == 0) and
             (on_segment(self.endpoint1, segment.endpoint1, self.endpoint2) or on_segment(self.endpoint1, segment.endpoint2, self.endpoint2) or
                on_segment(segment.endpoint1, self.endpoint1, segment.endpoint2) or on_segment(segment.endpoint1, self.endpoint2, segment.endpoint2))):
            return True

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


# Class that represents a single vertex
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

    # Returns True if vertex lies above the segment
    #         False if vertex lies underneath the segment
    def is_above(self, segment):
        return orientation(segment.point1, segment.point2, self) == 2


# Class that represents the DAG
class DagNode:
    def __init__(self, content, left_child, right_child, parent):
        self.content = content
        self.left_child = left_child
        self.right_child = right_child
        self.parent = parent

    # Choose which child is the successor for the point location search
    def choose_next(self, point):
        if isinstance(self.content, Trapezoid):
            return self
        elif isinstance(self.content, Vertex):
            return self.left_child if self.content.orientation(point) == -1 else self.right_child
        elif isinstance(self.content, Segment):
            return self.left_child if orientation(self.content.endpoint1, self.content.endpoint2, point) == 1 else self.right_child
        else:
            assert(False, "DagNode: Encountered content of unexpected instance %s" % type(self.content).__name__)
            return None

    # Set left child
    def set_left_child(self, content):
        self.left_child = DagNode(content, None, None, self)

    # Set right child
    def set_right_child(self, content):
        self.right_child = DagNode(content, None, None, self)


# Class that represents the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self, bounding_box):
        self.dag = DagNode(bounding_box, None, None, None)

    # Finds and returns the trapezoid in which the requested point lies
    def find_point_location(self, point):
        current_node = self.dag
        while not isinstance(current_node.content, Trapezoid):
            current_node = current_node.choose_next(point)
        return current_node

    # Finds all trapezoids that intersect the segment
    def find_intersecting_trapezoids(self, segment):
        start_trapezoid = self.find_point_location(segment.endpoint1)
        end_trapezoid = self.find_point_location(segment.endpoint2)

        intersected_trapezoids = [start_trapezoid]
        current_trapezoid = start_trapezoid
        while not current_trapezoid == end_trapezoid:
            # go to the next trapezoid on the path
            for trap in current_trapezoid.neighbours:
                if trap.intersects_segment(segment):
                    #found successor
                    intersected_trapezoids.append(trap)
                    current_trapezoid = trap
                    break
        return intersected_trapezoids

    # Adds a new segment to the vertical decomposition if it does not intersect
    # Returns True if segment could be inserted in this vertical decomposition
    #         False if segment could not be inserted in this vertical decomposition
    def add_segment(self, segment):
        intersecting_trapezoids = self.find_intersecting_trapezoids(segment)

        intersection_found = False
        for trapezoid in intersecting_trapezoids:
            # Checks if the segment has an intersection with the bottom segment of the trapezoid
            if trapezoid.find_intersection(segment):
                intersection_found = True

        if intersection_found:
            return False

        # Add segment to DAG
        self.update(intersecting_trapezoids, segment)
        return True

    # Updates the DAG with the new trapezoids induced by adding segment
    def update(self, trapezoids, segment):
        # todo: handle same x-coordinate degenerate cases in case trapezoid has multiple left or right points
        new_trapezoids, carry = [], None
        if len(trapezoids) == 1:
            # Segment is completely contained in a single trapezoid
            trapezoid = trapezoids[0]

            # Replace trapezoid with four trapezoids
            trapezoid1 = Trapezoid(trapezoid.top_segment, trapezoid.left_points, segment.endpoint1, trapezoid.bottom_segment)
            trapezoid2 = Trapezoid(trapezoid.top_segment, segment.endpoint1, segment.endpoint2, segment)
            trapezoid3 = Trapezoid(segment, segment.endpoint1, segment.endpoint2, trapezoid.bottom_segment)
            trapezoid4 = Trapezoid(trapezoid.top_segment, segment.endpoint2, trapezoid.right_point, trapezoid.bottom_segment)

            # update the dag
            parent_node = trapezoid.parent
            if parent_node.left_child.content == trapezoid:
                parent_node.set_left_child(segment.endpoint1)
                lp_node = parent_node.left_child
            else:
                parent_node.set_right(segment.endpoint1)
                lp_node = parent_node.right_child

            lp_node.set_left_child(trapezoid1)
            lp_node.set_right_child(segment.endpoint2)
            lp_node.set_right_child(trapezoid4)
            lp_node.right_child.set_left_child(segment)
            segment_node = lp_node.right_child.left_child
            segment_node.set_left_child(trapezoid3)
            segment_node.set_right_child(trapezoid2)

            new_trapezoids.extend([trapezoid1, trapezoid2, trapezoid3, trapezoid4])
        else:
            for trapezoid in trapezoids:
                if trapezoid.contains(segment.endpoint1):
                    # Replace trapezoid with three trapezoids
                    trapezoid1 = Trapezoid(trapezoid.top_segment, trapezoid.left_point, segment.endpoint1, trapezoid.bottom_segment)
                    trapezoid2 = Trapezoid(trapezoid.top_segment, segment.endpoint1,
                                           trapezoid.right_point if trapezoid.right_point.is_above(segment) else None,
                                           segment)
                    trapezoid3 = Trapezoid(segment, segment.endpoint1,
                                           trapezoid.right_point if not trapezoid.right_point.is_above(segment) else None,
                                           trapezoid.bottom_segment)

                    carry = trapezoid2 if trapezoid2.right_point is None else trapezoid3
                    new_trapezoids.extend(list(filter(lambda item: item != carry, [trapezoid1, trapezoid2, trapezoid3])))

                    # update the dag
                    parent_node = trapezoid.parent
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

                elif trapezoid.contains(segment.endpoint2):
                    assert(carry is not None, "VD: Expected a carry, but none found")

                    # Replace trapezoid with three trapezoids
                    trapezoid1 = Trapezoid(trapezoid.top_segment,
                                           trapezoid.left_point if trapezoid.left_point.is_above(segment) else carry.left_point,
                                           segment.endpoint2, segment)
                    trapezoid2 = Trapezoid(segment,
                                           trapezoid.left_point if not trapezoid.left_point.is_above(segment) else carry.left_point,
                                           segment.endpoint2, trapezoid.bottom_segment)
                    trapezoid3 = Trapezoid(trapezoid.top_segment, segment.endpoint2, trapezoid.right_point, trapezoid.bottom_segment)

                    new_trapezoids.extend([trapezoid1, trapezoid2, trapezoid3])

                    # update the dag
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
                    assert (carry is not None, "VD: Expected a carry, but none found")

                    # Replace trapezoid with two trapezoids
                    trapezoid1 = Trapezoid(trapezoid.top_segment,
                                           trapezoid.left_point if trapezoid.left_point.is_above(segment) else carry.left_point,
                                           trapezoid.right_point if trapezoid.right_point.is_above(segment) else None,
                                           segment)
                    trapezoid2 = Trapezoid(segment,
                                           trapezoid.left_point if not trapezoid.left_point.is_above(segment) else carry.left_point,
                                           trapezoid.right_point if not trapezoid.right_point.is_above(segment) else None,
                                           trapezoid.bottom_segment)

                    carry = trapezoid1 if trapezoid1.right_point is None else trapezoid2
                    new_trapezoids.extend(list(filter(lambda item: item != carry, [trapezoid1, trapezoid2])))

                    # update the dag
                    parent_node = trapezoid.parent
                    if parent_node.left_child.content == trapezoid:
                        parent_node.set_left_child(segment)
                        lp_node = parent_node.left_child
                    else:
                        parent_node.set_right(segment)
                        lp_node = parent_node.right_child

                    lp_node.set_right_child(trapezoid1)
                    lp_node.set_left_child(trapezoid2)



        # todo: update DAG (replace trapezoids with new_trapezoids)


# Incrementally build vertical decompositions of planar subgraphs
def main():
    # Read instance and instantiate graph, bounding box and starting vertical decomposition
    instance = read_instance(INPUT_FILE)  # read edges from input file
    g = instance["graph"]

    edges = g.edges
    random.shuffle(edges)  # Find random reordering of edges to decrease expected running time complexity

    bounding_box = find_bounding_box(g.nodes)
    vds = [VerticalDecomposition(bounding_box)]

    # Init output file
    file = open(OUTPUT_FILE, 'w')
    file.write("%d %d \n" % (len(edges), len(g.nodes)))
    file.close()

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
    left_top = Vertex(min_x - 1, max_y + 1)
    right_top = Vertex(max_x + 1, max_y + 1)
    left_bottom = Vertex(min_x - 1, min_y - 1)
    right_bottom = Vertex(max_x + 1, min_y + 1)

    return Trapezoid(Segment(left_top, right_top, None), left_bottom, right_top, Segment(left_bottom, right_bottom, None))


# Adds the intersection with segment to the output file
def add_intersection_to_output(bottom_segment, segment):
    file = open(OUTPUT_FILE, "a")
    file.write("%s %s \n" % (bottom_segment, segment))
    file.close()


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
