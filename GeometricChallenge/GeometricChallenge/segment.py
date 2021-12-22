import geometry


# Class that represents a single line segment between two vertices
class Segment:
    def __init__(self, endpoint1, endpoint2, face_above = None):
        self.endpoint1 = endpoint1 if endpoint1.x <= endpoint2.x else endpoint2
        self.endpoint2 = endpoint2 if endpoint1.x <= endpoint2.x else endpoint1
        self.face_above = face_above

    # Calculate intersection between the two segments
    def intersects(self, segment):
        # Find orientations
        orientation1 = geometry.orientation(self.endpoint1, self.endpoint2, segment.endpoint1)
        orientation2 = geometry.orientation(self.endpoint1, self.endpoint2, segment.endpoint2)
        orientation3 = geometry.orientation(segment.endpoint1, segment.endpoint2, self.endpoint1)
        orientation4 = geometry.orientation(segment.endpoint2, segment.endpoint2, self.endpoint2)

        # Segments should intersect if they overlap
        if ((orientation1 == geometry.CL and orientation2 == geometry.CL and orientation3 == geometry.CL and orientation4 == geometry.CL) and
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

        # Endpoint of one line situated on other line should not intersect
        if ((orientation1 == geometry.CL and geometry.on_segment(self.endpoint1, segment.endpoint1, self.endpoint2)) or
                (orientation2 == geometry.CL and geometry.on_segment(self.endpoint1, segment.endpoint2, self.endpoint2)) or
                (orientation3 == geometry.CL and geometry.on_segment(segment.endpoint1, self.endpoint1, segment.endpoint2)) or
                (orientation4 == geometry.CL and geometry.on_segment(segment.endpoint1, self.endpoint2, segment.endpoint2))):
            return False

        # Different orientations means lines intersect
        if (orientation1 != orientation2) and (orientation3 != orientation4):
            return True

        # All other cases do not intersect
        return False


