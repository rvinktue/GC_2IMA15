import geometry
import vertex


# function handles
orientation = geometry.orientation
on_segment_cl = geometry.on_segment


# Class that represents a single line segment between two vertices
class Segment:
    __slots__ = ('endpoint1', 'endpoint2', 'index', 'type')

    def __init__(self, endpoint1, endpoint2, index=-1):
        self.endpoint1 = endpoint1 if endpoint1.x <= endpoint2.x else endpoint2
        self.endpoint2 = endpoint2 if endpoint1.x <= endpoint2.x else endpoint1
        self.index = index
        self.type = geometry.SEGMENT

    def __str__(self):
        return f"(index: {self.index}, {self.endpoint1} -- {self.endpoint2})"

    # Calculate intersection between the two segments
    def intersects(self, segment: 'Segment') -> bool:
        # avoid dot
        _selfendpoint1 = self.endpoint1
        _selfendpoint2 = self.endpoint2
        _otherendpoint1 = segment.endpoint1
        _otherendpoint2 = segment.endpoint2

        # Find orientations
        orientation1 = orientation(_selfendpoint1, _selfendpoint2, _otherendpoint1)
        orientation2 = orientation(_selfendpoint1, _selfendpoint2, _otherendpoint2)
        orientation3 = orientation(_otherendpoint1, _otherendpoint2, _selfendpoint1)
        orientation4 = orientation(_otherendpoint1, _otherendpoint2, _selfendpoint2)

        # Segments should intersect if they overlap
        if ((orientation1 == geometry.CL and orientation2 == geometry.CL
             and orientation3 == geometry.CL and orientation4 == geometry.CL) and
                (on_segment_cl(_selfendpoint1, _otherendpoint1, _selfendpoint2) or
                 on_segment_cl(_selfendpoint1, _otherendpoint2, _selfendpoint2) or
                 on_segment_cl(_otherendpoint1, _selfendpoint1, _otherendpoint2) or
                 on_segment_cl(_otherendpoint1, _selfendpoint2, _otherendpoint2))):
            return True

        # Shared endpoint should not intersect
        if ((_selfendpoint1.x == _otherendpoint1.x and _selfendpoint1.y == _otherendpoint1.y) or
                (_selfendpoint2.x == _otherendpoint1.x and _selfendpoint2.y == _otherendpoint1.y) or
                (_selfendpoint1.x == _otherendpoint2.x and _selfendpoint1.y == _otherendpoint2.y) or
                (_selfendpoint2.x == _otherendpoint2.x and _selfendpoint2.y == _otherendpoint2.y)):
            return False

        # Different orientations means lines intersect
        if (orientation1 != orientation2) and (orientation3 != orientation4):
            return True

        # Endpoint of one line situated on other line should intersect
        if ((orientation1 == geometry.CL and on_segment_cl(_selfendpoint1, _otherendpoint1, _selfendpoint2)) or
                (orientation2 == geometry.CL and
                 on_segment_cl(_selfendpoint1, _otherendpoint2, _selfendpoint2)) or
                (orientation3 == geometry.CL and
                 on_segment_cl(_otherendpoint1, _selfendpoint1, _otherendpoint2)) or
                (orientation4 == geometry.CL and
                 on_segment_cl(_otherendpoint1, _selfendpoint2, _otherendpoint2))):
            return True

        # All other cases do not intersect
        return False

    # Calculate intersection between the two segments
    # Used for neighbours calculation
    def intersects_vertical(self, segment: 'Segment') -> bool:
        (a, b) = (self.endpoint1.y, self.endpoint2.y) \
            if self.endpoint1.y <= self.endpoint2.y \
            else (self.endpoint2.y, self.endpoint1.y)
        (c, d) = (segment.endpoint1.y, segment.endpoint2.y) \
            if segment.endpoint1.y <= segment.endpoint2.y \
            else (segment.endpoint2.y, segment.endpoint1.y)
        return max(a, c) < min(b, d)

    # Calculate intersection between segment and vertical boundary (self) of trapezoid
    def is_entered_by(self, segment: 'Segment') -> bool:
        # Find orientations
        orientation1 = orientation(self.endpoint1, self.endpoint2, segment.endpoint1)
        orientation2 = orientation(self.endpoint1, self.endpoint2, segment.endpoint2)
        orientation3 = orientation(segment.endpoint1, segment.endpoint2, self.endpoint1)
        orientation4 = orientation(segment.endpoint1, segment.endpoint2, self.endpoint2)

        # Different orientations means lines intersect
        if (orientation1 != orientation2) and (orientation3 != orientation4):
            return True

        # Shared endpoint should intersect
        if ((self.endpoint1.x == segment.endpoint1.x and self.endpoint1.y == segment.endpoint1.y) or
                (self.endpoint2.x == segment.endpoint1.x and self.endpoint2.y == segment.endpoint1.y) or
                (self.endpoint1.x == segment.endpoint2.x and self.endpoint1.y == segment.endpoint2.y) or
                (self.endpoint2.x == segment.endpoint2.x and self.endpoint2.y == segment.endpoint2.y)):
            return True

        # Endpoint of segment on boundary should intersect
        if ((orientation1 == geometry.CL and geometry.on_segment(self.endpoint1, segment.endpoint1, self.endpoint2)) or
                (orientation2 == geometry.CL and geometry.on_segment(self.endpoint1, segment.endpoint2, self.endpoint2))):
            return True



        # All other cases do not intersect
        return False

    def on_segment(self, point: vertex.Vertex) -> bool:
        """
        This method returns True if point lies on segment, False otherwise.
        We assume the segment is a vertical line.
        We assume the point is within trapezoid
        """
        return self.endpoint1.x == point.x

    def point_contained_vertical(self, point: vertex.Vertex) -> bool:
        return min(self.endpoint1.y, self.endpoint2.y) <= point.y <= max(self.endpoint1.y, self.endpoint2.y)
