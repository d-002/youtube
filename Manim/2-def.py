from manim import *
import numpy as np

from fast_voronoi import *
from fast_voronoi.neighbors import is_neighbor
from fast_voronoi.intersections import cells_intersections
from fast_voronoi.polygons import make_polygons
from fast_voronoi.utils import perp_bisector, get_equidistant

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        self.first_scene()
        self.second_scene()

    def first_scene(self):
        bounds = get_bounds(self.camera, 0)
        np.random.seed(0)
        cells = [Cell(v2(np.random.uniform(bounds.left+1, bounds.right-1),
                         np.random.uniform(bounds.top+1, bounds.bottom-1)))
                 for _ in range(50)]
        polygons, dots, colors = make_polygons_and_dots(
                cells, bounds, THEME1, theme_func_gradient)

        for polygon in polygons:
            polygon.set_stroke(opacity=0)

        neighbors = [[] for _ in range(len(cells))]
        for i in range(len(cells)):
            for j in range(len(cells)):
                if i == j:
                    continue

                if is_neighbor(bounds, cells, i, j):
                    neighbors[i].append(j)

        intersections = cells_intersections(bounds, cells, neighbors)
        vertices = VGroup(Dot((inter.pos.x, inter.pos.y, 0), color=FG, radius=.05)
                          for inter in intersections).set_z_index(1)

        self.play(FadeIn(polygons))
        self.wait()

        poly_simple = make_polygons(Options(), bounds, cells)

        edges = VGroup().set_z_index(1)
        for _, polygon in poly_simple:
            for i in range(len(polygon)):
                u, v = polygon[i-1], polygon[i]
                edges.add(Line((u.x, u.y, 0), (v.x, v.y, 0), color=FG))

        self.play(AnimationGroup(Write(vertices), Write(edges), lag_ratio=.5),
                  rate_func=linear, run_time=5)
        self.wait()

        everything = VGroup(polygons, vertices, edges)
        scale = 3
        shift = 2*RIGHT
        self.play(everything.animate.scale(scale).shift(shift))

        # find the cell that is closest to the center of the screen
        center_i = min(list(range(len(polygons))), key=lambda i: cells[i].pos.length())

        make_transparent = []
        for i, polygon in enumerate(polygons):
            if i != center_i:
                make_transparent.append(polygon.animate.set_fill(opacity=.2))

        self.play(AnimationGroup(make_transparent))
        self.wait()

        neighbors_i = neighbors[center_i][:2]
        A, B, C = cells[center_i], cells[neighbors_i[0]], cells[neighbors_i[1]]
        self.play(polygons[i].animate.set_fill(opacity=.5) for i in neighbors_i)
        self.wait()

        pos = get_equidistant(A.pos, B.pos, C.pos)
        circle = Circle(radius=.05, color=FG).move_to(
                np.array([pos.x, pos.y, 0])*scale + shift)
        self.add(circle)
        self.play(circle.animate.set_opacity(0).scale(20))
        self.remove(circle)
        self.wait()

        self.play(polygons[neighbors_i[1]].animate.set_fill(opacity=.2))
        edge = Line(*[np.array([inter.pos.x, inter.pos.y, 0])*scale + shift
                      for inter in intersections
                      if A in inter.cells and B in inter.cells], color=FG)
        self.add(edge)
        self.play(edge.animate.set_stroke(width=100).set_opacity(0))
        self.remove(edge)
        self.wait()

        center_vertices = VGroup(dot for i, dot in enumerate(vertices)
                                 if A in intersections[i].cells)
        other_vertices = VGroup(dot for i, dot in enumerate(vertices)
                                 if A not in intersections[i].cells)
        shift += 2*LEFT + UP
        self.play(everything.animate.shift(2*LEFT + UP))
        self.play((polygon.animate.set_fill(opacity=.2) for polygon in polygons),
                  Unwrite(edges),
                  Unwrite(other_vertices))

        wrong_polygon = Polygon(*[dot.get_center() for dot in center_vertices])
        wrong_polygon.set_fill(color="#FF0000", opacity=1)
        wrong_polygon.set_stroke(color=FG)
        self.wait()
        self.play(Write(wrong_polygon),
                  AnimationGroup(dot.animate.set_color(color="#FF0000")
                                 for dot in center_vertices),
                  run_time=3)
        self.wait()

        self.play(Unwrite(wrong_polygon), Unwrite(center_vertices))

        self.play(everything.animate.shift(-shift).scale(1/scale))
        self.play(FadeOut(polygons))
        self.wait(.3)

    def second_scene(self):
        bounds = get_bounds(self.camera, 0)
        np.random.seed(0)
        cells = [Cell(v2(np.random.uniform(bounds.left+1, bounds.right-1),
                         np.random.uniform(bounds.top+1, bounds.bottom-1)))
                 for _ in range(3)]
        A, B, C = cells
        polygons, dots, colors = make_polygons_and_dots(
                cells, bounds, THEME3, theme_func_gradient)

        self.play(FadeIn(polygons))

        point = Dot((-2, -1, 0), radius=.15, color=FG)
        self.play(Write(point))
        self.wait()

        bisector = perp_bisector(B.pos, C.pos)
        u = bisector.M + bisector.u * -2.5
        self.play(point.animate.move_to((u.x, u.y, 0)), run_time=2)
        self.wait()

        u = get_equidistant(A.pos, B.pos, C.pos)
        self.play(point.animate.move_to((u.x, u.y, 0)), run_time=2)
        self.wait()

        self.play(Unwrite(point), FadeOut(polygons), lag_ratio=.5, run_time=2)
