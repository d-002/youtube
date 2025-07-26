from manim import *

from theme import *
from utils import *

from fast_voronoi import *
from fast_voronoi.utils import perp_bisector, get_equidistant
from fast_voronoi.polygons import make_polygons

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        options = Options(segments_density=10, divide_lines=True, complete_polygons=True)
        bounds = get_bounds(self.camera, 0)
        left, top, w, h = bounds.left, bounds.top, bounds.w, bounds.h
        bounds = Bounds(left*3, top*3, w*3, h*3)

        cells = [Cell(v2(x, y), 1) for x, y in [(-5, -2), (4, 0), (0, h*1.5), (0, -h*1.5), (-w*1.5, 10)]]
        A, B, C = cells[:3]
        dots = VGroup(Dot(radius=.15, color=FG).move_to((cell.pos.x, cell.pos.y, 0))
                      for cell in cells)

        self.play(Write(dots))
        self.wait()

        bisector = perp_bisector(A.pos, B.pos)
        a, b = bisector.M - bisector.u*2, bisector.M + bisector.u*2

        segment = Line((a.x, a.y, 0), (b.x, b.y, 0), color=FG)
        self.play(Write(segment))
        self.wait()

        ends = get_ends_from_bisector(bounds, bisector)
        line = Line(*ends, color=FG)
        self.play(ReplacementTransform(segment, line))
        self.wait()

        dashed_line = DashedLine(*ends, color=FG, dash_length=.2).set_z_index(-1)
        self.add(dashed_line)
        self.remove(line)

        def cells_updater1(t):
            f = lambda t: 0 if t < 0 else 1 if t > 1 else rush_from(t)
            t2 = f(t*3)
            t3 = f(t*3-1)
            t4 = f(t*3-2)

            cells[2].pos.y = h*1.5 - t2*h*.8
            cells[3].pos.y = -h*1.5 + t3*h*.8
            cells[4].pos = v2(-w*1.5 * (1-t4), 10 * (1-t4))

        def cells_updater2(t):
            cells[2].pos = v2(-2*t, h*.7 - t*h*.3)
            cells[3].pos.y = -h*.7 - t*h*.8
            cells[4].pos = v2(-w*1.5 * t, 10*t)

        def cells_updater3(t):
            a = v2(-2, h*.4)
            b = v2(-7, -1)
            c = v2(0, 0)

            t *= 3
            if t < 1:
                cells[2].pos = a + (b-a) * smooth(t)
            elif t < 2:
                cells[2].pos = b + (c-b) * smooth(t-1)
            else:
                cells[2].pos = c + (a-c) * smooth(t-2)

        def cells_updater4(t):
            cells[2].pos.y = h*.4 + t*h*.2
            cells[3].pos.y = -h*1.5 + t*h*.7

        def cells_updater5(t):
            cells[2].pos.y = h*.6 - t*h*.2
            cells[3].pos.y = -h*.8 + t*h*.4
            cells[4].pos = v2(-w*1.5 * (1-t), 10 * (1-t))

        def style_polygon_wireframe(_, polygon, __):
            polygon.set_color(FG)
            polygon.set_fill(opacity=0)

        def style_polygon_t_filled(i, polygon, t):
            polygon.set_fill(color=[COL1, COL2, COL3, COL3, COL3][i], opacity=.5*t)
            polygon.set_stroke(FG)

        def style_polygon_filled(i, polygon, _):
            polygon.set_fill(color=[COL1, COL2, COL3, COL3, COL3][i], opacity=.5)
            polygon.set_stroke(FG)

        def polygons_updater(_):
            cells_updater(t.get_value())

            index = 0
            for i, points_raw in make_polygons(options, bounds, cells):
                points = [(u.x, u.y, 0) for u in points_raw]

                polygon = polygons[index]
                polygon.set_points_as_corners(points)
                polygon.set_opacity(1)
                style_polygon(i, polygon, t.get_value())

                index += 1

            # hide the unused polygons
            for i, polygon in enumerate(polygons):
                polygons[i].set_opacity(i < index)

        def dots_updater(_):
            for cell, dot in zip(cells, dots):
                u = cell.pos
                dot.move_to((u.x, u.y, 0))

        cells_updater = style_polygon = None
        t = ValueTracker(0)

        def play_animation(_cells_updater, _style_polygon, **kwargs):
            nonlocal cells_updater, style_polygon
            cells_updater = _cells_updater
            style_polygon = _style_polygon

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

        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        polygons = VGroup(Polygon(*dummy) for _ in range(len(cells)))
        self.add(polygons)

        play_animation(cells_updater1, style_polygon_wireframe, rate_func=linear, run_time=5)
        self.wait()

        play_animation(lambda _: None, style_polygon_t_filled)

        play_animation(cells_updater2, style_polygon_filled, run_time=3)
        self.wait()

        inter = get_equidistant(A.pos, B.pos, C.pos)
        inter = (inter.x, inter.y, 0)
        circle = Circle(radius=.05, color=FG).move_to(inter)
        self.add(circle)
        self.play(circle.animate.scale(20).set_opacity(0), run_time=.5)
        self.remove(circle)
        self.wait()

        play_animation(cells_updater3, style_polygon_filled, rate_func=linear, run_time=6)
        self.wait()

        for half in Line(inter, ends[0], color=FG), Line(inter, ends[1], color=FG):
            self.add(half)
            self.play(half.animate.set_stroke(width=100).set_opacity(0))
            self.remove(half)
        self.wait()

        everything = VGroup(polygons, dots, dashed_line)
        scale, shift = 1.5, np.array((1, 3, 0))
        self.play(everything.animate.scale(scale).shift(shift), run_time=2)
        self.wait()
        move = (2, -5, 0)
        shift += move
        self.play(everything.animate.shift(move))
        self.wait()
        self.play(everything.animate.shift(-shift).scale(1/scale), run_time=2)
        self.wait()

        play_animation(cells_updater4, style_polygon_filled, rate_func=rush_from)
        self.wait()
        play_animation(cells_updater5, style_polygon_filled, rate_func=rush_from)
        self.wait()

        self.play(everything.animate.scale(.7), FadeOut(dashed_line))
        everything -= dashed_line
        self.wait()

        for cell in cells:
            cell.pos *= .7
        bounds = get_bounds(self.camera, 100)
        cells_updater = lambda _: None
        polygons_updater(None)

        self.play(everything.animate.scale(.1))
        self.wait()
        self.play(everything.animate.scale(10))
        self.wait()

        def bounds_updater(_):
            nonlocal bounds
            bounds = get_bounds(self.camera, .1 - t.get_value())

        polygons.add_updater(bounds_updater)
        play_animation(lambda _: None, style_polygon_filled, run_time=4)
        self.wait()
