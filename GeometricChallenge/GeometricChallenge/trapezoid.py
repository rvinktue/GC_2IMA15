import segment as seg_type


# Class that represents a single Trapezoid in the Vertical Decomposition
class Trapezoid:
    def __init__(self, top_segment, left_points, right_points, bottom_segment):
        self.top_segment = top_segment
        self.left_points = left_points
        self.right_points = right_points
        self.bottom_segment = bottom_segment
        # Update bottom segment reference
        bottom_segment.face_above = self

    def find_intersection(self, segment):
        # Only compare with bottom segment. If it also intersects top segment,
        # then the intersection will be added when we evaluate the corresponding
        # trapezoid as segment will also intersect that trapezoid.
        if self.bottom_segment.intersects(segment):
            return self.bottom_segment

        return None

    # Returns True if the segment crosses this trapezoid
    #         False otherwise
    def intersects_segment(self, segment):
        # If segment crosses trapezoid, then it must cross one of the four boundaries
        return (self.bottom_segment.intersects(segment) or
                self.top_segment.intersects(segment) or
                seg_type.Segment(self.top_segment.endpoint1, self.bottom_segment.endpoint1, None).intersects(segment) or
                seg_type.Segment(self.top_segment.endpoint2, self.bottom_segment.endpoint2, None).intersects(segment))
