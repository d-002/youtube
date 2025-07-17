from manim import VGroup, Polygon, Dot
from fast_voronoi import Bounds, Options
from fast_voronoi.polygons import make_polygons

from theme import FG

def get_bounds(camera, margin):
    cx, cy = camera.frame_center[:2]
    w, h = camera.frame_width, camera.frame_height
    x, y = cx-w/2, cy-h/2
    x, y, w, h = x-margin, y-margin, w+2*margin, h+2*margin

    return Bounds(x, y, w, h)

def make_polygons_and_dots(cells, bounds, colors):
    polygons = make_polygons(options, bounds, cells)
    polygons = VGroup(Polygon(*[(u.x, u.y, 0) for u in polygon]) for _, polygon in polygons)
    dots = VGroup(Dot((cell.pos.x, cell.pos.y, 0)).set_z_index(1) for cell in cells)
    for color, polygon in zip(colors, polygons):
        polygon.set_fill(color, opacity=1)
        polygon.set_stroke(FG)

    return polygons, dots

options = Options(segments_density=10, divide_lines=True)
