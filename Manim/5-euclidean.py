from manim import *

from theme import *
from utils import *

from fast_voronoi import *

import numpy as np

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        self.first_scene()
        self.clear()
        self.second_scene()
        self.clear()
        self.third_scene()
        self.clear()
        self.fourth_scene()
        self.clear()
        self.fifth_scene()
        self.clear()
        self.sixth_scene()

    def first_scene(self):
        svg = SVGMobject('resources/pythagoras.svg').scale_to_fit_height(6)
        img = ImageMobject('resources/pythagoras.jpg').scale_to_fit_height(6)

        self.play(Create(svg).set_run_time(3).set_rate_func(linear))
        alt = Text('Pythagoras', font_size=20).next_to(img, DOWN).shift(3*LEFT)
        self.play(FadeIn(img),
                  Write(alt),
                  svg.animate.shift(3*LEFT),
                  img.animate.shift(3*LEFT))

        a, b, c = (5.5, 0, 0), (2, 2, 0), (2, 0, 0)
        edges = [(b, c), (a, c), (a, b)]
        colors = [COL1, COL2, COL3]

        triangle = VGroup(Line(*edge, color=color)
                          for color, edge in zip(colors, edges))
        triangle += RightAngle(triangle[0], triangle[1], color=FG)

        offsets = [(.3, 0, 0), (0, .3, 0), (.2, .2, 0)]
        triangle += VGroup(Text(char, color=color, stroke_color=color, font_size=24)
                           .move_to((np.array(a)+b)/2 + offset)
                           for char, color, offset, (a, b)
                           in zip('abc', colors, offsets, edges))

        self.play(Write(triangle), run_time=2)
        self.wait()

        equation = VGroup(MathTex('c^2', font_size=48, color=COL3),
                          MathTex('=', font_size=48, color=FG),
                          MathTex('a^2', font_size=48, color=COL1),
                          MathTex('+', font_size=48, color=FG),
                          MathTex('b^2', font_size=48, color=COL2))
        equation.arrange(RIGHT, buff=.2).next_to(triangle, 2*DOWN)
        self.play(Write(equation[0]))
        self.wait()
        self.play(Write(equation[1:]), run_time=2)
        self.wait()

        self.play(svg.animate.shift(10*LEFT),
                  img.animate.shift(10*LEFT),
                  alt.animate.shift(10*LEFT),
                  triangle.animate.shift(8*RIGHT),
                  equation.animate.shift(8*RIGHT))
        self.wait()

    def squiggly_line(self, a, b):
        f = lambda t: np.reshape((t, np.sin(2*np.pi*t)*.2, 0), (3, 1))
        u = b-a
        start = np.reshape(a, (3, 1))
        mat = np.matrix([[u[0], -u[1], 0],
                         [u[1],  u[0], 0],
                         [0,     0,    1]])

        return [np.array((mat*f(t) + start).T)[0] for t in np.arange(0, 1+1e-6, .01)]

    def second_scene(self):
        a, b = np.array([-2, -1, 0]), np.array([2, 2, 0])
        c = np.array([b[0], a[1], 0])
        A = Dot(a, radius=.15, color=FG).set_z_index(1)
        B = Dot(b, radius=.15, color=FG).set_z_index(1)
        self.play(AnimationGroup(Write(A), Write(B), lag_ratio=.2), run_time=1.2)

        triangle = VGroup(Line(a, b, color=COL3, stroke_width=8),
                          Line(a, c, color=COL2, stroke_width=8),
                          Line(b, c, color=COL1, stroke_width=8),
                          Dot(c, radius=.08, color=FG).set_z_index(1))
        triangle += RightAngle(triangle[1], triangle[2], color=FG)

        self.play(Write(triangle[0]))
        self.wait()
        self.play(Write(triangle[1:]), lag_ratio=.5)
        self.wait()

        origin_offset = (-3, -2, 0)
        plane = NumberPlane(x_range=(-4.111111111111111, 10.111111111111111, 1),
                            y_range=(-2.0, 6.0, 1),
                            **number_plane_config)
        self.play(FadeIn(plane))
        self.wait()

        for m, shift, text, offset in ((triangle[1], -a, '4 units', DOWN),
                                       (triangle[2], -c, '3 units', LEFT)):
            shift += origin_offset
            color = m.get_color()
            text = Text(text, color=color, stroke_color=color)

            self.play(m.animate.shift(shift), run_time=.5)
            text.next_to(m, offset)
            self.play(FadeIn(text), run_time=.5)
            self.wait(.2)
            self.play(FadeOut(text), run_time=.5)
            self.play(m.animate.shift(-shift), run_time=.5)

        self.wait()
        self.play(FadeOut(plane))

        Tex.set_default(font_size=48, color=FG, buff=.2)
        m = MathTex('c^2', '=', 'a^2', '+', 'b^2').to_corner(UL).shift(DR)
        self.play(Write(m))
        n = MathTex('c^2', '=', '4^2', '+', 'b^2').move_to(m)
        self.play(ReplacementTransform(m, n))
        o = MathTex('c^2', '=', '4^2', '+', '3^2').move_to(n)
        self.play(ReplacementTransform(n, o))
        p = MathTex('c^2', '=', '16', '+', '9').move_to(o)
        self.play(ReplacementTransform(o, p))
        q = MathTex('c^2', '=', '25').move_to(p)
        self.play(TransformMatchingTex(p, q))
        r = MathTex('c', '=', '5').move_to(q)
        self.play(ReplacementTransform(q, r))
        s = MathTex('5',  font_size=64, color=COL3)
        s.move_to((a+b)/2 + UL*.4)
        self.play(ReplacementTransform(r, s))
        self.wait()

        self.play(FadeOut(triangle[1:], s))
        self.wait()

        points = self.squiggly_line(a, b)

        weird_line = VMobject(color=COL3, stroke_width=8)
        weird_line.set_points_as_corners(points)
        self.play(ReplacementTransform(triangle[0], weird_line))
        self.wait(.5)
        straight_line = Line(a, b, color=COL3, stroke_width=8)
        self.play(ReplacementTransform(weird_line, straight_line))
        self.wait()

        self.play(FadeOut(straight_line, A, B))

    def third_scene(self):
        svg = SVGMobject('resources/euclid.svg').scale_to_fit_height(6)
        img = ImageMobject('resources/euclid.png').scale_to_fit_height(6)

        self.play(Create(svg).set_run_time(5).set_rate_func(linear))
        self.wait()
        alt = Text('Euclid', font_size=20).next_to(img, DOWN).shift(3*RIGHT)
        self.play(FadeIn(img),
                  Write(alt),
                  svg.animate.shift(3*RIGHT),
                  img.animate.shift(3*RIGHT))
        self.wait()
        postulates = Text("Euclid's Postulates", font_size=48).shift(3*LEFT)
        self.play(FadeIn(postulates))
        self.wait()

        quote = Text("""
\"A straight
line segment
can be drawn
joining any
two points\"""", color=FG, font='Z003', font_size=48).shift(3*LEFT)
        self.play(FadeOut(postulates), run_time=.7)
        self.play(Write(quote))
        self.wait()

        self.play(FadeOut(quote))
        space = Text('Euclidean space', font_size=48).shift(3*LEFT)
        self.play(FadeIn(space))
        self.wait()

        quote = Text("""
\"No straight
line segment
can be drawn
joining any
two points\"""", color=FG, font='Z003', font_size=48).shift(3*LEFT)
        self.play(FadeOut(space))
        self.play(Write(quote))
        self.wait()

        self.play(quote.animate.shift(10*LEFT),
                  svg.animate.shift(10*RIGHT),
                  img.animate.shift(10*RIGHT),
                  alt.animate.shift(10*RIGHT))
        self.wait()

    def fourth_scene(self):
        theorem1 = MathTex('a^2', '+', 'b^2', '=', 'c^2', color=FG)
        self.play(Write(theorem1))
        self.wait()
        theorem2 = MathTex('a', '+', 'b', '=', 'c', color=FG)
        self.play(ReplacementTransform(theorem1, theorem2))
        self.wait()

        title = VGroup(
                Text('Euclidean distance', font_size=36, weight=BOLD).shift(3*LEFT+2*UP),
                Text('Manhattan distance', font_size=36, weight=BOLD).shift(3*RIGHT+2*UP))
        theorem3 = MathTex('a^2', '+', 'b^2', '=', 'c^2').shift(3*LEFT+DOWN)
        theorem4 = MathTex(r'\lvert a \rvert', '+', r'\lvert b \rvert', '=', r'\lvert c \rvert').shift(3*RIGHT+DOWN)
        self.add(theorem3)
        self.play(FadeIn(theorem3),
                  ReplacementTransform(theorem2, theorem4),
                  FadeIn(title))
        self.wait()
        self.play(FadeOut(theorem3, theorem4, title))
        self.wait()

    def fifth_scene(self):
        a = MathTex(r'\text{Cell}(x, y', ')', font_size=56, color=FG)
        self.play(FadeIn(a))
        self.wait()

        b = MathTex(r'\text{Cell}(x, y', ', weight', ')', font_size=56, color=FG)
        self.play(ReplacementTransform(a, b))
        self.wait()

        c = MathTex('dist =', 'dist_{euclidean}', color=FG)
        self.play(b.animate.shift(2*UP))
        self.play(FadeIn(c))
        self.wait()

        d = MathTex('dist =', r'weight \times', 'dist_{euclidean}', color=FG)
        self.play(ReplacementTransform(c, d))
        self.wait()

        self.play(FadeOut(b, d))

    def sixth_scene(self):
        self.wait()

        bounds = get_bounds(self.camera, 1)
        scale = 6
        left, top, w, h = bounds.left*scale, bounds.top, bounds.w*scale, bounds.h
        bounds = Bounds(left, top, w, h)

        np.random.seed(0)
        cells = [Cell(v2(np.random.random()*w+left, np.random.random()*h+top),
                      np.random.random()*3 + 2) for _ in range(100)]

        polygons, _, _ = make_polygons_and_dots(
                cells, bounds, THEME2, theme_func_gradient)
        for polygon in polygons:
            polygon.set_stroke_color(BG)
        polygons.shift(w*(scale-1)/scale/2*RIGHT)

        self.play(polygons.animate.shift(w*(scale-1)/scale*LEFT), rate_func=linear, run_time=20)
