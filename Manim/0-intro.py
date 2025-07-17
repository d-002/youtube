from random import seed, random
from math import pi, cos, sin
from manim import *
from fast_voronoi import *
from fast_voronoi.polygons import make_polygons

from theme import *
from utils import *


class VoronoiAnim:
    def __init__(self, bounds: Bounds, cells: list[Cell],
                 colors: list[tuple], style_funcs, show_dots: bool = False,
                 buffer: int = 10):
        self.bounds = bounds
        self.cells = cells
        self.colors = colors

        self.style_polygon, self.style_dot = style_funcs

        # could be a varying number of polygons per cell, so add a small buffer
        length = len(cells)+buffer
        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        self.polygons = VGroup(Polygon(*dummy) for _ in range(length))

        if show_dots:
            self.dots = VGroup(*(Dot((cell.pos.x, cell.pos.y, 0),
                                     radius=.2) for cell in cells))
        else:
            self.dots = VGroup()

        self.update()

    def update(self):
        polygons = make_polygons(options, self.bounds, self.cells)

        index = 0
        for i, points_raw in polygons:
            dots = [(u.x, u.y, 0) for u in points_raw]

            if index >= len(self.polygons):
                raise ValueError('Not enough polygons in VoronoiAnim buffer')
            polygon = self.polygons[index]

            # hard-code hide polygon if too small
            if len(dots) < 5:
                polygon.set_opacity(0)
            else:
                polygon.set_points_as_corners(dots)
                polygon.set_opacity(1) # fallback
                self.style_polygon(polygon, self.colors[i])

            index += 1

        # hide the unused polygons
        for i in range(index, len(self.polygons)):
            self.polygons[i].set_opacity(0)

        for i, dot in enumerate(self.dots):
            self.style_dot(dot, self.colors[i])
            u = self.cells[i].pos
            dot.move_to((u.x, u.y, 0))

    def play(self, scene: Scene, func, **kwargs):
        def updater(_):
            func(self, t.get_value())
            self.update()

        t = ValueTracker(0)
        self.polygons.add_updater(updater)
        scene.play(t.animate.set_value(1), **kwargs)
        self.polygons.clear_updaters()


class Dance:
    def __init__(self, camera):
        self.bounds = get_bounds(camera, 20)

    def init1(self, voronoi):
        black, white = voronoi.cells[:2]
        black.pos = v2(self.bounds.right/4, 0)
        white.pos = v2(self.bounds.left*.7, 0)
        black.weight = 1
        white.weight = 1

        for i in range(2, len(voronoi.cells)):
            cell = voronoi.cells[i]
            cell.weight = 100
            cell.pos = v2(self.bounds.left, i)

        voronoi.update()

    def arrive1(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = (1-t) * self.bounds.right/2
        white.weight = 5 - 4*t

    def arrive2(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = t * (.1*self.bounds.right)
        white.pos.x = (.7-t*.6) * self.bounds.left

    def close(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = (t*.05 + .1)*self.bounds.right
        white.pos.x = (1-t) * (.1*self.bounds.left)

    def updown(self, voronoi, t):
        white = voronoi.cells[1]
        white.pos.y = t * (.1*self.bounds.bottom)

    def rotate(self, voronoi, t):
        black, white = voronoi.cells[:2]

        a1 = (3*pi) * max(0, t*1.05 - .05) # black (lag)
        a2 = 3*pi*t + pi # white
        radius = .1*self.bounds.right

        black.pos = v2(cos(a1), -sin(a1))*radius
        white.pos = v2(cos(a2), -sin(a2))*radius

    def init3(self, voronoi):
        black, white, green = voronoi.cells[:3]

        black.pos = v2(.1*self.bounds.left, 0)
        white.pos = v2(.1*self.bounds.right, 0)

        green.weight = 1
        green.pos = v2(0, self.bounds.top/2)
        voronoi.update()

    def arrive3(self, voronoi, t):
        black, white, green = voronoi.cells[:3]

        y = t * .075*self.bounds.bottom
        black.pos.y = y
        white.pos.y = y

        green.pos.y = (1 - t*.9) * self.bounds.top/2

    def cut(self, voronoi, t):
        black, white, green = voronoi.cells[:3]

        y = (1 - 2*t) * .075*self.bounds.bottom
        black.pos.y = y
        white.pos.y = y

        green.pos.y = (1 - 2*t) * .05*self.bounds.top

    def init_all(self, voronoi):
        seed(0)

        for cell in voronoi.cells[3:]:
            cell.weight = 1

            x, y = random()-.5, random()-.5
            x += -.3 if x < 0 else .3
            y += -.3 if y < 0 else .3
            cell.pos = v2(x*self.bounds.right/2, y*self.bounds.bottom/2)

        # ugly but works
        for cell in voronoi.cells:
            cell.base_pos = cell.pos

        voronoi.update()

    def arrive_everything(self, voronoi, t):
        scale = 1 / (1+t)
        for cell in voronoi.cells:
            cell.pos = cell.base_pos*scale

    def weight(self, voronoi, t):
        for i, cell in enumerate(voronoi.cells):
            if i == 0:
                weight = 5
            elif i == 1:
                weight = 1
            else:
                weight = 10

            cell.weight = t * (weight-1) + 1

    def disappear_other(self, voronoi, t):
        weight = 10 + 100*t
        opacity = 1-t

        for cell in voronoi.cells[2:]:
            cell.weight = weight
        for dot in voronoi.dots[2:]:
            dot.set_opacity(opacity)

    def init_swap(self, voronoi):
        for cell in voronoi.cells[:2]:
            cell.base_pos = cell.pos

        for i in range(len(voronoi.cells)):
            cell = voronoi.cells[i]
            cell.pos = v2(self.bounds.left, i)

    def swap(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.weight = 5 - t*4
        white.weight = 1 + t*4

        offset = white.base_pos * -t
        opacity = 1-t

        for cell in voronoi.cells[:2]:
            cell.pos = cell.base_pos + offset
        for dot in voronoi.dots[:2]:
            dot.set_opacity(opacity)

    def disappear_last(self, voronoi, t):
        white = voronoi.cells[1]
        white.weight = 5 + 100*t

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG)
        self.camera.background_color = BG

        def style_poly_transparent(polygon: Polygon, color: tuple):
            polygon.set_stroke(color)
            polygon.set_fill(color, opacity=.5)

        def style_poly_fill(polygon: Polygon, color: tuple):
            polygon.set_stroke(width=0)
            polygon.set_fill(color, opacity=1)

        def style_dot_invert(dot: Dot, color: ManimColor):
            r, g, b = color.to_rgb()
            r, g, b = int(r*255), int(g*255), int(b*255)

            if r+g+b < 384:
                r, g, b = min(r+50, 255), min(g+50, 255), min(b+50, 255)
            else:
                r, g, b = max(r-50, 0), max(g-50, 0), max(b-50, 0)

            dot.set_color(ManimColor.from_rgb((r, g, b)))

        def style_none(_, __):
            pass

        dance = Dance(self.camera)
        bounds = dance.bounds

        cells = [Cell(v2(i, 0), 1) for i in range(8)]
        colors = [BG, FG, GRAY, COL1, COL2, COL3, COL4, COL5]

        funcs = style_poly_fill, style_dot_invert
        voronoi = VoronoiAnim(bounds, cells, colors, funcs, True)

        text1 = Text('Headphones recommended', font_size=20)
        text1.set_stroke(FG)
        self.play(Write(text1, run_time=2))
        self.wait(1)
        self.play(FadeOut(text1, run_time=5))

        self.add(voronoi.polygons)
        self.add(voronoi.dots)
        dance.init1(voronoi)

        voronoi.play(self, dance.arrive1, run_time=2, rate_func=rush_from)
        self.wait(1.5)
        voronoi.play(self, dance.arrive2, run_time=4, rate_func=double_smooth)
        self.wait(2.5)
        voronoi.play(self, dance.close, run_time=2, rate_func=there_and_back)
        self.wait(1.5)
        voronoi.play(self, dance.close, run_time=1, rate_func=there_and_back)
        self.wait(.5)
        voronoi.play(self, dance.updown, run_time=4, rate_func=there_and_back)
        self.wait(1.5)
        voronoi.play(self, dance.rotate, run_time=5)
        text2 = Text('A presentation by D_00', font_size=30)
        text2.set_stroke(FG)
        text2.to_corner(UL)
        self.play(Create(text2), run_time=1.5)

        dance.init3(voronoi)

        voronoi.play(self, dance.arrive3, run_time=4, rate_func=double_smooth)
        self.play(FadeOut(text2), run_time=1)
        voronoi.play(self, dance.cut, run_time=5, rate_func=there_and_back)
        self.wait(.5)

        everything = VGroup(voronoi.polygons, voronoi.dots)
        self.play(FadeOut(everything), run_time=1)
        dance.init_all(voronoi)
        self.play(FadeIn(everything), run_time=1)
        self.wait(1)
        voronoi.play(self, dance.arrive_everything, run_time=3)
        self.wait(2)

        voronoi.play(self, dance.weight, run_time=7)
        voronoi.style_poly = voronoi.style_dot = style_none
        voronoi.play(self, dance.disappear_other, run_time=1)
        voronoi.style_poly, voronoi.style_dot = style_poly_fill, style_dot_invert
        self.wait(.5)
        dance.init_swap(voronoi)
        voronoi.play(self, dance.swap, run_time=3)
        title = VGroup(Text('The beauty of', font_size=40, stroke_color=FG).shift(UP),
                       Text('Voronoi diagrams', font_size=40, stroke_color=FG).shift(DOWN),
                       Text('#SoME4', color=GRAY, font_size=20, stroke_color=GRAY).shift(1.5*DOWN))
        self.play(Write(title), run_time=1.5, lag_ratio=.5)
        voronoi.play(self, dance.disappear_last, run_time=1.5, rate_func=lambda t: 1-slow_into(1-t))
        self.wait(.5)
        self.play(FadeOut(title), run_time=2)
