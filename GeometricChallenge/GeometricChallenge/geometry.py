import vertex
import segment
import trapezoid

# Returns 0 if the three points are collinear,
#         1 if traversing the points in order of arguments given makes a right turn (clockwise)
#        -1 if traversing the points in order of arguments given makes a left turn (counterclockwise)
COLLINEAR = CL = 0
CLOCKWISE = CW = 1
COUNTERCLOCKWISE = CCW = -1


def orientation(point1, point2, point3):
    val = (float(point2.y - point1.y) * (point3.x - point2.x)) - (float(point2.x - point1.x) * (point3.y - point2.y))
    if val > 0:
        return CW  # Clockwise
    elif val < 0:
        return CCW  # Counterclockwise
    else:
        return CL  # Collinear


# Checks if point2 is contained on the line segment with endpoints point1 and point3
# where we assume the three points are collinear
def on_segment(point1, point2, point3):
    if ((point2.x <= max(point1.x, point3.x)) and (point2.x >= min(point1.x, point3.x)) and
            (point2.y <= max(point1.y, point3.y)) and (point2.y >= min(point1.y, point3.y))):
        return True
    return False


# Returns a bounding box for the set of nodes as a trapezoid
def find_bounding_box(nodes):
    min_x = min_y = 1e10
    max_x = max_y = -1e10
    for node in nodes:
        min_x, min_y, max_x, max_y = min(node.x, min_x), min(node.y, min_y), max(node.x, max_x), max(node.y, max_y)

    # Build the trapezoid of the bounding box
    left_top = vertex.Vertex(min_x - 1, max_y + 1)
    right_top = vertex.Vertex(max_x + 1, max_y + 1)
    left_bottom = vertex.Vertex(min_x - 1, min_y - 1)
    right_bottom = vertex.Vertex(max_x + 1, min_y - 1)

    return trapezoid.Trapezoid(segment.Segment(left_top, right_top, None), left_bottom, right_top, segment.Segment(left_bottom, right_bottom, None))

