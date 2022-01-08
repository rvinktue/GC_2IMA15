import geometry
import vertex


# Class that represents a single line segment between two vertices
class Segment:
    def __init__(self, endpoint1, endpoint2, face_above=None, index=-1):
        self.endpoint1 = endpoint1 if endpoint1.x <= endpoint2.x else endpoint2
        self.endpoint2 = endpoint2 if endpoint1.x <= endpoint2.x else endpoint1
        self.face_above = face_above
        self.index = index

    # Calculate intersection between the two segments
    def intersects(self, segment: 'Segment') -> bool:
        # Find orientations
        orientation1 = geometry.orientation(self.endpoint1, self.endpoint2, segment.endpoint1)
        orientation2 = geometry.orientation(self.endpoint1, self.endpoint2, segment.endpoint2)
        orientation3 = geometry.orientation(segment.endpoint1, segment.endpoint2, self.endpoint1)
        orientation4 = geometry.orientation(segment.endpoint1, segment.endpoint2, self.endpoint2)

        # Segments should intersect if they overlap
        if ((orientation1 == geometry.CL and orientation2 == geometry.CL
             and orientation3 == geometry.CL and orientation4 == geometry.CL) and
                (geometry.on_segment(self.endpoint1, segment.endpoint1, self.endpoint2) or
                 geometry.on_segment(self.endpoint1, segment.endpoint2, self.endpoint2) or
                 geometry.on_segment(segment.endpoint1, self.endpoint1, segment.endpoint2) or
                 geometry.on_segment(segment.endpoint1, self.endpoint2, segment.endpoint2))):
            return True

        # Shared endpoint should not intersect
        if ((self.endpoint1.x == segment.endpoint1.x and self.endpoint1.y == segment.endpoint1.y) or
                (self.endpoint2.x == segment.endpoint1.x and self.endpoint2.y == segment.endpoint1.y) or
                (self.endpoint1.x == segment.endpoint2.x and self.endpoint1.y == segment.endpoint2.y) or
                (self.endpoint2.x == segment.endpoint2.x and self.endpoint2.y == segment.endpoint2.y)):
            return False

        # Endpoint of one line situated on other line should intersect
        if ((orientation1 == geometry.CL and geometry.on_segment(self.endpoint1, segment.endpoint1, self.endpoint2)) or
                (orientation2 == geometry.CL and
                 geometry.on_segment(self.endpoint1, segment.endpoint2, self.endpoint2)) or
                (orientation3 == geometry.CL and
                 geometry.on_segment(segment.endpoint1, self.endpoint1, segment.endpoint2)) or
                (orientation4 == geometry.CL and
                 geometry.on_segment(segment.endpoint1, self.endpoint2, segment.endpoint2))):
            return True

        # Different orientations means lines intersect
        if (orientation1 != orientation2) and (orientation3 != orientation4):
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
        orientation1 = geometry.orientation(self.endpoint1, self.endpoint2, segment.endpoint1)
        orientation2 = geometry.orientation(self.endpoint1, self.endpoint2, segment.endpoint2)
        orientation3 = geometry.orientation(segment.endpoint1, segment.endpoint2, self.endpoint1)
        orientation4 = geometry.orientation(segment.endpoint1, segment.endpoint2, self.endpoint2)

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

        # Different orientations means lines intersect
        if (orientation1 != orientation2) and (orientation3 != orientation4):
            return True

        # All other cases do not intersect
        return False

    def on_segment(self, point: vertex.Vertex) -> bool:
        """
        This method returns True if point lies on segment, False otherwise.
        We assume the segment is a vertical line.
        """
        return self.endpoint1.x == point.x
