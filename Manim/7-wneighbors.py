from manim import *

from theme import *
from utils import *

from fast_voronoi import *
from fast_voronoi.utils import get_circle, circle_inter

import numpy as np

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        options = Options(segments_density=10, divide_lines=True, complete_polygons=True)
        bounds = get_bounds(self.camera, 1)
        left, top, w, h = bounds.left, bounds.top, bounds.w, bounds.h
        bounds = Bounds(left*3, top*3, w*3, h*3)

        cells = [Cell(v2(x, y), w) for x, y, w in [(-5, -2, 1), (4, 0, 1.5), (0, h*1.5, 3), (1, -h*1.5, 4)]]
        A, B, C = cells[:3]
        dots = VGroup(Dot(radius=.15, color=FG).move_to((cell.pos.x, cell.pos.y, 0))
                      for cell in cells)

        circle = get_circle(cells[0], cells[1])
        circle = Circle(np.sqrt(circle.r2), color=FG).move_to(
                (circle.c.x, circle.c.y, 0))
        circle = DashedVMobject(circle, num_dashes=200)

        def cells_updater1(t):
            f = lambda t: 0 if t < 0 else 1 if t > 1 else rush_from(t)
            t2 = f(t*2)
            t3 = f(t*2-1)

            cells[2].pos.y = h*1.5 - t2*h*1.2
            cells[3].pos.y = -h*1.5 + t3*h*1.2

        def cells_updater2(t):
            cells[2].weight = 3 - 2.5*t
            cells[3].weight = 4 - t

        def cells_updater3(t):
            cells[2].pos.y = h*.3 + t*h*1.2
            cells[3].pos.y = -h*.3 - t*h*1.2

        def polygons_updater(_):
            cells_updater(t.get_value())

            index = 0
            for i, points_raw in make_polygons(options, bounds, cells):
                points = [(u.x, u.y, 0) for u in points_raw]

                polygon = polygons[index]
                polygon.set_points_as_corners(points)

                index += 1

            # hide the unused polygons
            for i in range(index, len(polygons)):
                polygons[i].set_opacity(0)

        cells_updater = None
        t = ValueTracker(0)

        def play_animation(_cells_updater, **kwargs):
            nonlocal cells_updater
            cells_updater = _cells_updater

            t.set_value(0)

            dots.add_updater(dots_updater)
            polygons.add_updater(polygons_updater)
            self.play(t.animate.set_value(1), **kwargs)
            dots.clear_updaters()
            polygons.clear_updaters()

            # make sure the last frame of the animation is played
            t.set_value(1)
            polygons_updater(None)
            dots_updater(None)

        def dots_updater(_):
            for cell, dot in zip(cells, dots):
                u = cell.pos
                dot.move_to((u.x, u.y, 0))

        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        buffer = 5
        polygons = VGroup(Polygon(*dummy, fill_opacity=0, stroke_color=FG)
                          for _ in range(len(cells)+buffer))
        cells_updater = cells_updater1
        polygons_updater(None)

        self.play(Write(dots), FadeIn(polygons))
        self.add(circle)
        self.wait()

        play_animation(cells_updater1, rate_func=linear, run_time=5)
        self.wait()

        play_animation(cells_updater2, rate_func=there_and_back, run_time=5)
        t.set_value(0)
        polygons_updater(None)
        self.wait()

        play_animation(cells_updater3, run_time=.5)
        self.wait()

        play_animation(cells_updater1, rate_func=linear, run_time=2)
        self.wait()

        cab = get_circle(cells[0], cells[1])
        cac = get_circle(cells[0], cells[2])
        cad = get_circle(cells[0], cells[3])
        iabc = circle_inter(cab, cac)
        iabd = circle_inter(cab, cad)
        vertices = [min(iabc, key=lambda u: u.y), max(iabd, key=lambda u: u.y)]
        vertices = [Circle(radius=.05, color=COL1).move_to((u.x, u.y, 0))
                    for u in vertices]

        self.play(AnimationGroup((v.animate.set_opacity(0).scale(20)
                                 for v in vertices), lag_ratio=.5),
                  run_time=1.5)
        self.wait()

        self.play(FadeOut(circle, dots, polygons))
