import geometry


# Class that represents a single vertex
class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = geometry.VERTEX

    # Returns 0 if they share their x-coordinate
    #         1 if this vertex lies to the left of point
    #        -1 if this vertex lies to the right of point
    def x_order(self, point: 'Vertex') -> int:
        if self.x == point.x:
            return 0
        else:
            return 1 if point.x > self.x else -1

    # Returns True if vertex lies above the segment
    #         False if vertex lies underneath the segment
    def is_above(self, segment) -> bool:
        return geometry.orientation(segment.endpoint1, segment.endpoint2, self) != geometry.CLOCKWISE

    def is_below(self, segment) -> bool:
        return geometry.orientation(segment.endpoint1, segment.endpoint2, self) != geometry.CCW

