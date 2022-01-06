import segment as segclass
import vertex as vertclass


# Class that represents a single Trapezoid in the Vertical Decomposition
class Trapezoid:
    def __init__(self, top_segment, left_points, right_points, bottom_segment):
        self.top_segment = top_segment
        if isinstance(left_points, vertclass.Vertex):
            self.left_points = [left_points]
        else:
            self.left_points = list(set(left_points[:]))
        if isinstance(right_points, vertclass.Vertex):
            self.right_points = [right_points]
        else:
            self.right_points = list(set(right_points[:]))
        self.bottom_segment = bottom_segment
        # Update bottom segment reference
        bottom_segment.face_above = self

        if self.top_segment.endpoint1.x == self.top_segment.endpoint2.x:
            bottom_vertex = self.top_segment.endpoint1 \
                if self.top_segment.endpoint1.y <= self.top_segment.endpoint2.y \
                else self.top_segment.endpoint2
            self.top_segment = segclass.Segment(bottom_vertex, bottom_vertex)

        if self.bottom_segment.endpoint1.x == self.bottom_segment.endpoint2.x:
            top_vertex = self.bottom_segment.endpoint1 \
                if self.bottom_segment.endpoint1.y >= self.bottom_segment.endpoint2.y \
                else self.bottom_segment.endpoint2
            self.bottom_segment = segclass.Segment(top_vertex, top_vertex)

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

        p_top = vertclass.Vertex(px, max(a.y, b.y) if a.x == b.x else (a.y - b.y) / (a.x - b.x) * (px - a.x) + a.y)
        p_bot = vertclass.Vertex(px, min(c.y, d.y) if c.x == d.x else (d.y - c.y) / (d.x - c.x) * (px - d.x) + d.y)

        q_top = vertclass.Vertex(qx, max(a.y, b.y) if a.x == b.x else (a.y - b.y) / (a.x - b.x) * (qx - a.x) + a.y)
        q_bot = vertclass.Vertex(qx, min(c.y, d.y) if c.x == d.x else (d.y - c.y) / (d.x - c.x) * (qx - d.x) + d.y)

        self.left_segment = segclass.Segment(p_bot, p_top)
        self.right_segment = segclass.Segment(q_bot, q_top)

    def segment_enter(self, segment):
        return self.left_segment.is_entered_by(segment)

    def update_left_points(self, new_points):
        self.left_points = new_points[:]

        # Precompute quad and left/right segments
        a = self.top_segment.endpoint1
        b = self.top_segment.endpoint2
        c = self.bottom_segment.endpoint2
        d = self.bottom_segment.endpoint1

        if len(self.left_points) > 0:
            px = self.left_points[0].x
        else:
            px = max(a.x, d.x)

        p_top = vertclass.Vertex(px, max(a.y, b.y) if a.x == b.x else (a.y - b.y) / (a.x - b.x) * (px - a.x) + a.y)
        p_bot = vertclass.Vertex(px, min(c.y, d.y) if c.x == d.x else (d.y - c.y) / (d.x - c.x) * (px - d.x) + d.y)

        self.left_segment = segclass.Segment(p_bot, p_top)

    # Returns True if the segment crosses top or bottom boundary of this trapezoid
    #         False otherwise
    def is_violated_by_segment(self, segment):
        for boundary in [self.bottom_segment, self.top_segment]:
            if boundary.intersects(segment):
                return True

        return False

    def contains(self, point):
        return point.is_above(self.bottom_segment) and \
               not point.is_above(self.top_segment) \
               and self.left_segment.endpoint1.x <= point.x <= self.right_segment.endpoint1.x
