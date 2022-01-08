from __future__ import annotations
import typing
import segment as segclass
import vertex as vertclass
import geometry


# Class that represents a single Trapezoid in the Vertical Decomposition
class Trapezoid:
    # __slots__ = ('top_segment', 'left_points', 'right_points', 'bottom_segment', 'type', 'left_segment', 'right_segment')

    def __init__(self, top_segment, left_points, right_points, bottom_segment) -> None:
        self.top_segment = top_segment
        self.left_points = left_points
        self.right_points = right_points
        self.bottom_segment = bottom_segment
        self.type = geometry.TRAPEZOID

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
            px = next(iter(self.left_points)).x
        else:
            px = max(a.x, d.x)
        if len(self.right_points) > 0:
            qx = next(iter(self.right_points)).x
        else:
            qx = min(b.x, c.x)

        p_top = vertclass.Vertex(px, max(a.y, b.y) if a.x == b.x else (a.y - b.y) / (a.x - b.x) * (px - a.x) + a.y)
        p_bot = vertclass.Vertex(px, min(c.y, d.y) if c.x == d.x else (d.y - c.y) / (d.x - c.x) * (px - d.x) + d.y)

        q_top = vertclass.Vertex(qx, max(a.y, b.y) if a.x == b.x else (a.y - b.y) / (a.x - b.x) * (qx - a.x) + a.y)
        q_bot = vertclass.Vertex(qx, min(c.y, d.y) if c.x == d.x else (d.y - c.y) / (d.x - c.x) * (qx - d.x) + d.y)

        self.left_segment = segclass.Segment(p_bot, p_top)
        self.right_segment = segclass.Segment(q_bot, q_top)

    def segment_enter(self, segment: segclass.Segment) -> bool:
        return self.left_segment.is_entered_by(segment)

    def update_left_points(self, new_points: typing.Set[vertclass.Vertex]) -> None:
        self.left_points = new_points

        # Precompute quad and left/right segments
        a = self.top_segment.endpoint1
        b = self.top_segment.endpoint2
        c = self.bottom_segment.endpoint2
        d = self.bottom_segment.endpoint1

        if len(self.left_points) > 0:
            px = next(iter(self.left_points)).x
        else:
            px = max(a.x, d.x)

        p_top = vertclass.Vertex(px, max(a.y, b.y) if a.x == b.x else (a.y - b.y) / (a.x - b.x) * (px - a.x) + a.y)
        p_bot = vertclass.Vertex(px, min(c.y, d.y) if c.x == d.x else (d.y - c.y) / (d.x - c.x) * (px - d.x) + d.y)

        self.left_segment = segclass.Segment(p_bot, p_top)

    # Returns True if the segment crosses top or bottom boundary of this trapezoid
    #         False otherwise
    def is_violated_by_segment(self, segment: segclass.Segment) -> bool:
        for boundary in [self.bottom_segment, self.top_segment]:
            if boundary.intersects(segment):
                return True

        return False

    def contains(self, point: vertclass.Vertex) -> bool:
        return point.is_above(self.bottom_segment) and \
               not point.is_above(self.top_segment) \
               and self.left_segment.endpoint1.x <= point.x <= self.right_segment.endpoint1.x

    def is_valid(self, vertex: vertclass.Vertex) -> bool:
        if (self.top_segment.endpoint1.x == vertex.x and self.top_segment.endpoint1.y == vertex.y) != \
                (self.top_segment.endpoint2.x == vertex.x and self.top_segment.endpoint2.y == vertex.y) or \
                (self.bottom_segment.endpoint1.x == vertex.x and self.bottom_segment.endpoint1.y == vertex.y) != \
                (self.bottom_segment.endpoint2.x == vertex.x and self.bottom_segment.endpoint2.y == vertex.y):
            return True

        orientation1 = geometry.orientation(self.top_segment.endpoint1, self.top_segment.endpoint2, vertex)
        orientation2 = geometry.orientation(self.bottom_segment.endpoint1, self.bottom_segment.endpoint2, vertex)

        return not orientation1 == geometry.CL and not orientation2 == geometry.CL
