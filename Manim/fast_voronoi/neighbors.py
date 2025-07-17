from math import cos, sin, atan2, tau, sqrt

from .utils import smol, dot, get_t, get_closest_to_line, perp_bisector, \
        get_equidistant, get_dist2, get_circle, circle_inter, circle_inter_line

from .classes.v2 import v2
from .classes.cell import Cell
from .classes.line import Line
from .classes.bounds import Bounds
from .classes.circle import Circle
from .classes.block_manager import StraightBlockManager, CircleBlockManager


def cut_line_line(A: Cell, B: Cell, P: Cell, line1: Line,
                  manager: StraightBlockManager) -> bool:
    """
    Computes how a line edge between two cells A and B is affected by
    another line edge.
    Affects the given manager, but also returns True if the whole line
    gets blocked, False otherwise.
    """

    X = get_equidistant(A.pos, B.pos, P.pos)

    if X is None:
        # edge case where A, B and P are aligned
        # intersection point impossible
        # in this case, either P doesn't affect anything, or it
        # blocks the entire thing
        # depending on the ordering of the points

        if dot(v2(P.pos.x-A.pos.x, P.pos.y-A.pos.y),
               v2(P.pos.x-B.pos.x, P.pos.y-B.pos.y)) < 0:
            # P is between A and B
            return True
        return False

    # get how far down the line this point is
    t = get_t(line1, X)

    # get which bound is being modified by looking at
    # which side of (AB) P is
    H = get_closest_to_line(line1, P.pos)
    t_side = get_t(line1, H)

    if t_side < 0:
        manager.block_min(t)
    else:
        manager.block_max(t)

    return manager.is_blocked


def cut_line_circle(A: Cell, P: Cell, line1: Line,
                    manager: StraightBlockManager) -> bool:
    """
    Computes how a line edge between two cells A and B is affected by
    another circle edge.
    Affects the given manager, but also returns True if the whole line
    gets blocked, False otherwise.
    """

    circle2 = get_circle(A, P)
    intersections = circle_inter_line(line1, circle2)

    if not intersections:
        # only block if the circle is around A
        return A.weight > P.weight

    t0 = get_t(line1, intersections[0])
    t1 = get_t(line1, intersections[1])

    if t0 > t1:
        t0, t1 = t1, t0

    # circle around P: block the range between the two points
    if A.weight < P.weight:
        manager.add_block((t0, t1))

    # circle around A: block two ranges outside of the two points
    else:
        manager.block_min(t0)
        manager.block_max(t1)

    return manager.is_blocked


def cut_circle_line_inner(circle: Circle, line: Line, towards_other: v2,
                          manager: CircleBlockManager) -> bool:
    """
    Inner part of the circle/line blocking algorithm, used to compute
    intersection where the line is already known, for example with bounds.
    towards_other: vector indicating which side of the line goes towards
    the side that should be blocked.
    """

    intersections = circle_inter_line(line, circle)

    if len(intersections) < 2:
        return False

    # block a part of the circle

    da = intersections[0]-circle.c
    db = intersections[1]-circle.c
    a_a = atan2(da.y, da.x)
    a_b = atan2(db.y, db.x)

    if a_b < a_a:
        a_b += tau

    # find which side of the circle is blocked by checking which arc is
    # farthest into P (dot product with vector from A to B is positive)

    # create a test point in the arc between a_a and a_b
    a_mid = (a_a+a_b) / 2
    test_point = line.M + v2(cos(a_mid), sin(a_mid))

    if dot(test_point-line.M, towards_other) > 0:
        manager.add_block((a_a, a_b))
    else:
        manager.add_block((a_b, a_a+tau))

    return manager.is_blocked


def cut_circle_line(A: Cell, P: Cell, circle1: Circle,
                    manager: CircleBlockManager) -> bool:
    """
    Computes how a circle edge between two cells A and B is affected by
    another line edge.
    Affects the given manager, but also returns True if the whole circle
    gets blocked, False otherwise.
    """

    line2 = perp_bisector(A.pos, P.pos)

    return cut_circle_line_inner(circle1, line2, P.pos-A.pos, manager)


def cut_circle_bounds(circle: Circle, box: Bounds,
                      manager: CircleBlockManager):
    """
    Use bounds to block some parts of the circle
    from a circle block manager
    """

    for line, u in box.lines:
        cut_circle_line_inner(circle, line, u, manager)


def cut_circle_circle(A: Cell, P: Cell, circle1: Circle,
                      manager: CircleBlockManager) -> bool:
    """
    Computes how a circle edge between two cells A and B is affected by
    another circle edge.
    Affects the given manager, but also returns True if the whole circle
    gets blocked, False otherwise.
    """

    circle2 = get_circle(A, P)
    intersections = circle_inter(circle1, circle2)

    """
    if len(intersections) < 2:
        if circle2.r2 < circle1.r2:
            if get_dist2(A.pos, P.pos) > circle1.r2 \
                    and A.weight < P.weight:
                continue

            if A.weight < P.weight:
                continue
            return False

        continue
    """
    if len(intersections) < 2:
        return circle2.r2 < circle1.r2 and A.weight > P.weight

    # compute which side of the circle will be blocked, depending on
    # where P is: find the center of the arc created by the block,
    # and see whether it is closer than the original edge

    da = intersections[0]-circle1.c
    db = intersections[1]-circle1.c
    a_a = atan2(da.y, da.x)
    a_b = atan2(db.y, db.x)

    if a_b < a_a:
        a_b += tau

    a_mid = (a_a+a_b) / 2
    mid = circle1.c + v2(cos(a_mid), sin(a_mid)) * sqrt(circle1.r2)

    # flip condition if the other circle is centered around A, as
    # that means the incut part of the edge is the one that is the
    # most outside of the second circle instead of inside
    cond = get_dist2(circle2.c, mid) < circle2.r2
    cond ^= A.weight >= P.weight

    manager.add_block((a_a, a_b) if cond else (a_b, a_a+tau))

    return manager.is_blocked


def is_neighbor(bounds: Bounds, cells: list[Cell], i: int, j: int) -> bool:
    """
    Checks if the cells inside cells at indices i and j are neighbors
    """
    if i == j:
        return False

    A, B = cells[i], cells[j]

    # base edge is a line
    if abs(A.weight - B.weight) < smol:
        line1 = perp_bisector(A.pos, B.pos)
        manager = StraightBlockManager(line1, bounds)

        for k, P in enumerate(cells):
            if i == k or j == k:
                continue

            # other edge is also a line
            if abs(A.weight - P.weight) < smol:
                if cut_line_line(A, B, P, line1, manager):
                    return False

            # other edge is a circle
            else:
                if cut_line_circle(A, P, line1, manager):
                    return False

    # base edge is a circle
    else:

        # make sure the circle is centered around A: first, so that the
        # measured curvature is the one that is conditioned by the weight of
        # the node that is inside the circle, and second, because other
        # computations identify A as the node that is inside the circle for
        # easier logic
        if A.weight < B.weight:
            A, B = B, A

        circle1 = get_circle(A, B)
        manager = CircleBlockManager()
        cut_circle_bounds(circle1, bounds, manager)

        for k, P in enumerate(cells):
            if i == k or j == k:
                continue

            # other edge is a line
            if abs(A.weight - P.weight) < smol:
                if cut_circle_line(A, P, circle1, manager):
                    return False

            # other edge is also a circle
            else:
                if cut_circle_circle(A, P, circle1, manager):
                    return False

    return True
