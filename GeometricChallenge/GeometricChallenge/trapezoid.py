import segment as seg_type
import vertex as vertclass


# Class that represents a single Trapezoid in the Vertical Decomposition
class Trapezoid:
    def __init__(self, top_segment, left_points, right_points, bottom_segment):
        self.top_segment = top_segment
        if isinstance(left_points, vertclass.Vertex):
            self.left_points = [left_points]
        else:
            self.left_points = left_points
        if isinstance(right_points, vertclass.Vertex):
            self.right_points = [right_points]
        else:
            self.right_points = right_points
        self.bottom_segment = bottom_segment
        # Update bottom segment reference
        bottom_segment.face_above = self

        # Precompute quad and left/right segments
        a = self.top_segment.endpoint1
        b = self.top_segment.endpoint2
        c = self.bottom_segment.endpoint2
        d = self.bottom_segment.endpoint1

        if len(self.left_points) > 0:
            px = self.left_points[0].x
        else:
            px = max(a.x, d.x)
        if len(self.right_points) > 0:
            qx = self.right_points[0].x
        else:
            qx = min(b.x, c.x)

        p_top = vertclass.Vertex(px, (a.y - b.y) / (a.x - b.x) * (px - a.x) + a.y)
        p_bot = vertclass.Vertex(px, (d.y - c.y) / (d.x - c.x) * (px - d.x) + d.y)

        q_top = vertclass.Vertex(qx, (a.y - b.y) / (a.x - b.x) * (qx - a.x) + a.y)
        q_bot = vertclass.Vertex(qx, (d.y - c.y) / (d.x - c.x) * (qx - d.x) + d.y)

        self.left_segment = seg_type.Segment(p_bot, p_top)
        self.right_segment = seg_type.Segment(q_bot, q_top)

    def find_intersection(self, segment):
        # Only compare with bottom segment. If it also intersects top segment,
        # then the intersection will be added when we evaluate the corresponding
        # trapezoid as segment will also intersect that trapezoid.
        if self.bottom_segment.intersects(segment):
            return self.bottom_segment

        return None

    def segment_enter(self, segment):
        return self.left_segment.intersects(segment)

    # Returns True if the segment crosses this trapezoid
    #         False otherwise
    def intersects_segment(self, segment):
        # If segment crosses trapezoid, then it must cross one of the four boundaries
        return (self.bottom_segment.intersects(segment) or
                self.top_segment.intersects(segment) or
                self.left_segment.intersects(segment) or
                self.right_segment.intersects(segment))

    def contains(self, point):
        return point.is_above(self.bottom_segment) and \
               not point.is_above(self.top_segment) \
               and self.left_segment.endpoint1.x <= point.x <= self.right_segment.endpoint1.x
