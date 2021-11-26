import sympy
import cgshop2022utils.verify as cgv
from random import random


def test_do_intersect_regression1():
    s1 = cgv.Segment(cgv.Point(9528, 6418), cgv.Point(8306, 8082))
    s2 = cgv.Segment(cgv.Point(8306, 8082), cgv.Point(9261, 5941))
    assert not cgv.do_intersect(s1, s2)
    assert not cgv.do_intersect(s2, s1)


def test_do_intersect_vs_sympy(rounds=10000, s=100):
    for _ in range(rounds):
        s1x, s1y = int(round(s * random())), int(round(s*random()))
        t1x, t1y = int(round(s * random())), int(round(s*random()))
        s2x, s2y = int(round(s * random())), int(round(s*random()))
        t2x, t2y = int(round(s * random())), int(round(s*random()))
        if s1x == t1x and s1y == t1y:
            continue
        if s2x == t2x and s2y == t2y:
            continue
        s0 = sympy.Segment((s1x, s1y), (t1x, t1y))
        s1 = sympy.Segment((s2x, s2y), (t2x, t2y))
        cgs0 = cgv.Segment(cgv.Point(s1x, s1y), cgv.Point(t1x, t1y))
        cgs1 = cgv.Segment(cgv.Point(s2x, s2y), cgv.Point(t2x, t2y))
        sym_int = s0.intersection(s1)
        rf = cgv.do_intersect(cgs0, cgs1)
        rb = cgv.do_intersect(cgs1, cgs0)
        if rf is None:
            assert rb is None
        else:
            assert rb is not None
        if not sym_int:
            assert cgv.do_intersect(cgs0, cgs1) is None
        else:
            if not rf:
                if isinstance(sym_int, sympy.FiniteSet):
                    sym_int = list(sym_int)
                    assert isinstance(sym_int, list)
                    assert len(sym_int) == 1
                    assert isinstance(sym_int[0], sympy.Point2D)
                    xx, xy = sym_int[0].args
                    assert (xx, xy) in ((s1x,s1y), (s2x,s2y), (t1x,t1y), (t2x,t2y))
            else:
                if isinstance(sym_int, sympy.FiniteSet):
                    sym_int = list(sym_int)
                if isinstance(sym_int, list) and len(sym_int) == 1 and isinstance(sym_int[0], sympy.Point2D):
                    xx, xy = sym_int[0].args
                    sqdist = (xx-rf[0])**2 + (xy-rf[1])**2
                    assert sqdist <= 1e-13

