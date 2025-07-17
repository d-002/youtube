from manim import VGroup, Polygon, Dot
from copy import deepcopy
import numpy as np

from fast_voronoi import Bounds, Options
from fast_voronoi.polygons import make_polygons

from theme import FG

def get_bounds(camera, margin):
    cx, cy = camera.frame_center[:2]
    w, h = camera.frame_width, camera.frame_height
    x, y = cx-w/2, cy-h/2
    x, y, w, h = x-margin, y-margin, w+2*margin, h+2*margin

    return Bounds(x, y, w, h)

def get_color_from_t(colors, t):
    return colors[min(max(int(t*len(colors)), 0), len(colors)-1)]

smol = 1e-9
def get_ends_from_bisector(box, line):
    bounds: list[float] = [0]*4

    if abs(line.u.x) > smol:
        bounds[0] = (box.left-line.M.x) / line.u.x
        bounds[1] = (box.right-line.M.x) / line.u.x
    if abs(line.u.y) > smol:
        bounds[2] = (box.top-line.M.y) / line.u.y
        bounds[3] = (box.bottom-line.M.y) / line.u.y

    if abs(line.u.x) > smol:
        if abs(line.u.y) > smol:
            bounds.sort()

            tmin = max(bounds[:2])
            tmax = min(bounds[2:])
        else:
            tmin, tmax = sorted(bounds[:2])
    else:
        tmin, tmax = sorted(bounds[2:])

    u, v = line.M + line.u*tmin, line.M + line.u*tmax
    return (u.x, u.y, 0), (v.x, v.y, 0)

def make_polygons_and_dots(cells, bounds, colors, theme=None):
    """if theme is None, assign the colors by index and return polygons+dots
    otherwise, use theme as a function to choose a color in colors, and return
    polygons, dots, and a list of colors"""

    polygons = make_polygons(options, bounds, cells, False)
    polygons = VGroup(Polygon(*[(u.x, u.y, 0) for u in polygon]) for _, polygon in polygons)
    dots = VGroup(Dot((cell.pos.x, cell.pos.y, 0)).set_z_index(1) for cell in cells)

    new_colors = []
    for i, polygon in enumerate(polygons):
        if theme is None:
            color = colors[i]
        else:
            color = get_color_from_t(colors, theme(bounds, cells[i]))
            new_colors.append(color)

        polygon.set_fill(color, opacity=1)
        polygon.set_stroke(FG)

    if theme is None:
        return polygons, dots
    return polygons, dots, new_colors

def add_polygons_margin(dots, polygons, margin):
    """Warning: may not work for weighted Voronoi polygons"""

    def find(arr, target):
        for i, elt in enumerate(arr):
            if np.array_equal(elt, target):
                return i

        raise IndexError(f'find: {target} not found')

    for center, polygon in zip(dots, polygons):
        center = center.get_center()

        # fix the rotation direction
        a, b = polygon.points[:2]
        rotated = center-b
        rotated = np.array([-rotated[1], rotated[0], 0])
        if np.dot(b-a, rotated) > 0:
            polygon.points = np.flip(polygon.points)

        # add a margin
        points = deepcopy(polygon.points)
        for i, now in enumerate(points):
            before, after = points[i-1], points[(i+1) % len(points)]

            move = after-before
            move = np.array([-move[1], move[0], move[2]])
            move *= 1 / np.sqrt(np.sum(move**2))

            polygon.points[i] += move * margin

        # remove excess points (that make it go the other way)
        dist_sort = lambda pos: -np.sum((pos-center)**2)
        points_l = list(polygon.points)
        for now in sorted(polygon.points, key=dist_sort):
            i = find(points_l, now)
            before = points[i-1]

            rotated = center-now
            rotated = np.array([-rotated[1], rotated[0], 0])
            if np.dot(now-before, rotated) > 0:
                points_l.pop(i)

        polygon.points = np.array(points_l)

options = Options(segments_density=10, divide_lines=True)
