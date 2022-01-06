import vertex as vertclass


# Tests adding segment contained in single Trapezoid
# Tests adding segment contained in a left Trapezoid and a right Trapezoid
# Tests adding segment contained in a left Trapezoid, a middle Trapezoid and a right Trapezoid
def test_case_1():
    return [vertclass.Vertex(5, 1), vertclass.Vertex(10, 1),
            vertclass.Vertex(1, 3), vertclass.Vertex(6, 3),
            vertclass.Vertex(3, 2), vertclass.Vertex(8, 2),
            ]


# Tests degenerate case: lines with same x-coordinates
def test_case_2():
    return [vertclass.Vertex(1, 1), vertclass.Vertex(5, 1),
            vertclass.Vertex(1, 3), vertclass.Vertex(3, 3),
            ]


# Tests degenerate case: shared endpoints
def test_case_3():
    return [vertclass.Vertex(1, 1), vertclass.Vertex(10, 1),
            vertclass.Vertex(1, 1), vertclass.Vertex(5, 5),
            vertclass.Vertex(5, 5), vertclass.Vertex(10, 1),
            ]


# Tests degenerate case: vertical line
def test_case_4():
    return [vertclass.Vertex(2, 1), vertclass.Vertex(2, 5),
            vertclass.Vertex(1, 3), vertclass.Vertex(3, 3)
            ]

# @TODO: add some more (degenerate) test cases
