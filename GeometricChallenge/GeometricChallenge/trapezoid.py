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

    def segment_enter(self, segment):
        return self.left_segment.intersects(segment)

    # Returns True if the segment crosses top or bottom boundary of this trapezoid
    #         False otherwise
    def is_violated_by_segment(self, segment):
        for boundary in [self.bottom_segment, self.top_segment]:
            if boundary.intersects(segment):
                print("Intersection found between (%s, %s) -> (%s, %s) and (%s, %s) -> (%s, %s)"
                      % (boundary.endpoint1.x, boundary.endpoint1.y, boundary.endpoint2.x, boundary.endpoint2.y,
                         segment.endpoint1.x, segment.endpoint1.y, segment.endpoint2.x, segment.endpoint2.y))
                return True
        return False

    def contains(self, point):
        return point.is_above(self.bottom_segment) and \
               not point.is_above(self.top_segment) \
               and self.left_segment.endpoint1.x <= point.x <= self.right_segment.endpoint1.x
