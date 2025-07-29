from manim import *

from theme import *
from utils import *
from texx import *

import numpy as np

from fast_voronoi import *
from fast_voronoi.neighbors import is_neighbor
from fast_voronoi.intersections import cells_intersections
from fast_voronoi.polygons import make_polygons

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        self.first_scene()
        self.clear()
        self.second_scene()
        self.clear()
        self.third_scene()

    def stick_draw(self, sticks, center, radius, draw_circle=True, **kwargs):
        t = ValueTracker(0)
        segments = 100

        def circle_updater(_):
            angle = t.get_value()*2*np.pi

            if angle:
                points = [center + (np.cos(angle*t/segments)*radius,
                                    np.sin(angle*t/segments)*radius, 0)
                          for t in range(segments+1)]
                circle.set_points_as_corners(points)

        def sticks_updater(_):
            angle = t.get_value()*2*np.pi

            pos = center + (np.cos(angle)*radius, np.sin(angle)*radius, 0)
            for stick in sticks:
                stick.put_start_and_end_on(stick.get_start(), pos)

        sticks.add_updater(sticks_updater)
        if draw_circle:
            circle = VMobject(color=FG)
            circle.add_updater(circle_updater)
            self.add(circle)

        self.play(t.animate.set_value(1), **kwargs)

        sticks.clear_updaters()
        if draw_circle:
            circle.clear_updaters()
            return circle

    def first_scene(self):
        a = Text('Voronoi diagrams')
        self.play(Write(a), run_time=1.5)
        self.wait()
        b = Text('Weighted Voronoi diagrams')
        self.play(ReplacementTransform(a, b))
        self.wait()

        self.play(FadeOut(b), rate_func=linear, run_time=15)

        svg = SVGMobject('resources/apollonius.svg').scale_to_fit_height(5.5)
        svg.shift(.1*UP+.25*RIGHT)
        img = ImageMobject('resources/apollonius.png').scale_to_fit_height(6)

        self.play(Create(svg).set_run_time(5).set_rate_func(linear))
        alt = Text('Apollonius of Perga', font_size=20).next_to(img, DOWN)
        self.play(FadeIn(img),
                  Write(alt))
        self.wait()

        what = Text('What is a circle?', font_size=56).shift(10*LEFT)
        self.add(what)
        self.play(what.animate.shift(10*RIGHT),
                  svg.animate.shift(12*RIGHT),
                  img.animate.shift(12*RIGHT),
                  alt.animate.shift(12*RIGHT))
        self.remove(svg, alt)
        self.wait()

        self.play(FadeOut(what))

        center = VGroup(Dot(color=FG), Text('C').shift(.4*UR)).set_z_index(1)
        self.play(Write(center))
        circle = Circle(radius=2, color=FG)
        self.play(Write(circle))
        self.wait()
        self.play(Unwrite(circle))
        self.remove(circle)

        sticks = VGroup(Line(ORIGIN, (2, 0, 0), stroke_width=10, color=COL3)).set_z_index(1)
        self.play(Create(sticks))
        self.wait()
        circle = self.stick_draw(sticks, ORIGIN, 2, rate_func=smoothstep, run_time=4)
        self.wait()

        self.play(Unwrite(center), FadeOut(circle), Uncreate(sticks))
        self.wait()

        A, B = LEFT, 2*RIGHT
        centers = VGroup(Dot(color=COL3).move_to(A), Dot(color=COL1).move_to(B)).set_z_index(1)
        centers += Text('A', color=COL3, stroke_color=COL3).next_to(centers[0], .4*UR)
        centers += Text('B', color=COL1, stroke_color=COL1).next_to(centers[1], .4*UR)
        self.play(Write(centers))
        self.wait()

        sticks = VGroup(Line(A, A+(0, 1, 0), stroke_width=10, color=COL3),
                        Line(B, B+(0, 2, 0), stroke_width=10, color=COL1)).set_z_index(1)
        self.play(Write(sticks))
        self.wait()

        self.play(sticks.animate.stretch(1.5, dim=1, about_point=A))
        self.play(sticks.animate.stretch(.5, dim=1, about_point=A))
        self.play(sticks.animate.stretch(4/3, dim=1, about_point=A))
        self.wait()

        self.play(sticks[0].animate.put_start_and_end_on(A, ORIGIN))
        self.play(sticks[1].animate.put_start_and_end_on(B, ORIGIN))
        self.wait()

        circle = self.stick_draw(sticks, np.array([-2, 0, 0]), 2, False, run_time=4)
        self.wait()

        circle = self.stick_draw(sticks, np.array([-2, 0, 0]), 2, run_time=6)
        self.wait()

        main_diagram = VGroup(centers, circle, sticks)
        title = Text('Circle of Apollonius').to_edge(UP).shift(.5*DOWN)

        self.play(main_diagram.animate.shift(DOWN),
                  FadeIn(title))
        A, B = A+DOWN, B+DOWN
        self.wait()

        bounds = get_bounds(self.camera, 1)
        cells = [Cell(v2(A[0], A[1]), 1), Cell(v2(B[0], B[1]), 1)]

        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        polygons = VGroup(Polygon(*dummy) for _ in range(2))
        for polygon in polygons:
            polygon.set_fill(opacity=0)
            polygon.set_stroke(color=FG)
        self.add(polygons)

        def updater_ratio(_):
            ratio = t.get_value()

            # update cells
            wb = 1 / (1+ratio)
            wa = 1-wb
            cells[0].weight = wa
            cells[1].weight = wb

            # update "circle" (actually the boundary between the two cells)
            for i, points_raw in make_polygons(options, bounds, cells):
                points = [(u.x, u.y, 0) for u in points_raw]

                polygon = polygons[i]
                polygon.set_points_as_corners(points)

            # update sticks
            mid = A*wa + B*wb
            sticks[0].put_start_and_end_on(A, mid)
            sticks[1].put_start_and_end_on(B, mid)

        t = ValueTracker(2)
        updater_ratio(None)
        self.remove(circle)
        self.add(polygons)

        polygons.add_updater(updater_ratio)
        self.play(t.animate.set_value(3), run_time=2)
        self.play(t.animate.set_value(5/2), run_time=2)
        self.play(t.animate.set_value(1), FadeOut(title), run_time=2)
        self.wait()
        self.play(t.animate.set_value(1/3), run_time=1)
        self.play(t.animate.set_value(2), run_time=1.5)
        polygons.clear_updaters()
        self.wait()

        self.play(FadeOut(centers, sticks, polygons))
        self.wait()

    def second_scene(self):
        t2c.update({'w_A': COL1, 'w_B': COL2})
        Tex.set_default(tex_template=template)

        title = Tex('Finding the boundary made of points $P (x, y)$', font_size=48).to_edge(UP)
        self.play(FadeIn(title))

        a = Tex('between the cells $A$ and $B$:', color=GRAY)
        b = Texx('A (x_A, y_A, w_A)')
        c = Texx('B (x_B, y_B, w_B)')
        b.next_to(c, UP)
        a.next_to(b, UP)
        self.play(AnimationGroup(FadeIn(a), Write(b), Write(c), lag_ratio=.5))
        self.wait(.5)
        self.play(FadeOut(a, b, c))

        d = Tex('$P$ is defined as:', color=GRAY)
        e = Texx(r'w_A \lVert P-A \rVert', '=', r'w_B \lVert P-B \rVert')
        d.next_to(e, UP)
        self.play(AnimationGroup(FadeIn(d), Write(e), lag_ratio=.5))
        self.wait()

        f = Texx(r'w_A \lVert P-A \rVert', '-', r'w_B \lVert P-B \rVert', '= 0')
        self.play(FadeOut(d), ReplacementTransform(e, f))
        self.wait(.5)
        g = Texx(r'w_A \sqrt{(x-x_A)^2 + (y-y_A)^2}', '-', 'w_B \sqrt{(x-x_B)^2 + (y-y_B)^2}', '= 0')
        self.play(ReplacementTransform(f, g), run_time=1.5)
        self.wait(.5)
        h = Texx(r'w_A^2 ((x-x_A)^2 + (y-y_A)^2)', '-', 'w_B^2 ((x-x_B)^2 + (y-y_B)^2)', '= 0')
        self.play(ReplacementTransform(g, h))
        self.wait(.5)
        self.play(h.animate.to_edge(DOWN))

        main_board = VGroup(title, h)
        self.play(main_board.animate.shift(10*UP))
        h2 = Texx('w_A^2 ((x-x_A)^2', '+', '(y-y_A)^2)', '-', 'w_B^2 ((x-x_B)^2', '+', '(y-y_B)^2)', '=', '0').move_to(h)
        main_board -= h
        self.remove(h)
        main_board += h2
        self.add(h2)

        title2 = Tex('Finding a way to rewrite stuff for later', font_size=48).to_edge(UP)
        self.play(FadeIn(title2))
        self.wait(.5)

        j = Texx('a x^2 + b x', '=', r'\mu ((x-\alpha)^2', r'+ \gamma)')
        j2 = Texx('a x^2 + b x', '=', r'\mu ((x-\alpha)^2', r'+ \gamma)')
        comment = Tex(r'Finding $\mu, \alpha, \gamma$ so that:', color=GRAY).next_to(j, UP)
        self.play(Write(j), FadeIn(comment))
        self.wait(.5)
        self.add(j2)
        k = Texx('a x^2 + b x', '=', r'\mu x^2 - 2\alpha\mu x + \alpha^2', r'+ \gamma').next_to(j, DOWN)
        self.play(ReplacementTransform(j, k), FadeOut(comment))
        self.play(j2.animate.shift(2*UP), k.animate.shift(2*UP))
        self.wait(.5)

        l = Texx(r"""
\begin{cases}
    a = \mu \\
    b = 2\alpha\mu \\
    0 = \alpha^2 + \gamma
\end{cases}""").shift(DOWN)
        comment = Tex('Substitution', color=GRAY).next_to(l, UP)
        self.play(Write(l), FadeIn(comment))
        self.wait(.5)
        m = Texx(r"""\begin{cases}
    \mu = a \\
    \alpha = -\frac{b}{2 a} \\
    \gamma = -\frac{b^2}{4 a^2}
\end{cases}""").move_to(l)
        self.play(ReplacementTransform(l, m), FadeOut(comment))
        self.wait(.5)
        self.play(FadeOut(k), j2.animate.shift(DOWN))
        j3 = Texx('a x^2 + b x =', r'\mu', r'((x-\alpha)^2', r'+ \gamma)').shift(UP)
        self.remove(j2)
        self.add(j3)
        l = Texx('a x^2 + b x =', r'a', r'((x - \frac{b}{2 a})^2', r'- \frac{b^2}{4 a^2})').shift(UP)
        self.play(ReplacementTransform(j3, l))
        self.wait(.5)

        self.play(FadeOut(m), l.animate.shift(DOWN))
        self.wait(.5)
        m = Texx(r'a x^2 + b x = a ((x - \frac{b}{2 a})^2 - \frac{b^2}{4 a^2})')
        self.remove(l)
        self.add(m)
        self.play(main_board.animate.shift(10*DOWN),
                  title2.animate.shift(10*DOWN),
                  m.animate.shift(2*DOWN))
        self.remove(title2)

        self.play(h2.animate.move_to(ORIGIN), m.animate.to_edge(DOWN))
        self.wait(.5)
        n = Texx('w_A^2 (x-x_A)^2', '+', 'w_A^2 (y-y_A)^2', '-', 'w_B^2 (x-x_B)^2', '-', 'w_B^2 (y-y_B)^2', '=', '0', font_size=40)
        self.play(ReplacementTransform(h2, n))
        self.wait(.5)
        o = Texx('w_A^2 (x-x_A)^2', '-', 'w_B^2 (x-x_B)^2', '+', 'w_A^2 (y-y_A)^2', '-', 'w_B^2 (y-y_B)^2', '=', '0', font_size=40)
        self.play(ReplacementTransform(n, o))
        self.wait(.5)
        p = VGroup(Texx('w_A^2', '(x-x_A)^2', '-', 'w_B^2', '(x-x_B)^2'),
                   Texx('+', 'w_A^2', '(y-y_A)^2', '-', 'w_B^2', '(y-y_B)^2'),
                   Texx('= 0')).arrange(DOWN)
        self.play(ReplacementTransform(o, p))
        self.wait(.5)
        q = VGroup(Texx('w_A^2', '(x^2 - 2 x x_A + x_A^2)', '-', 'w_B^2', '(x^2 - 2 x x_B + x_B^2)'),
                   Texx('+', 'w_A^2', '(y^2 - 2 y y_A + y_A^2)', '-', 'w_B^2', '(y^2 - 2 y y_B + y_B^2)'),
                   Texx('= 0')).arrange(DOWN)
        self.play(ReplacementTransform(p, q))
        self.wait(.5)
        r = VGroup(Texx('w_A^2', '(x^2 - 2 x x_A)', '-', 'w_B^2', '(x^2 - 2 x x_B)'),
                   Texx('+ w_A^2', '(y^2 - 2 y y_A)', '-', 'w_B^2', '(y^2 - 2 y y_B)'),
                   Texx('+ w_A^2 x_A^2', '- w_B^2 x_B^2', '+ w_A^2 y_A^2', '- w_B^2 y_B^2', '= 0')).arrange(DOWN)
        self.play(ReplacementTransform(q, r))
        self.wait(.5)
        s = VGroup(Texx('w_A^2 x^2', '-', 'w_A^2 2 x x_A', '-', 'w_B^2 x^2', '+', 'w_B^2 2 x x_B'),
                   Texx('+ w_A^2 y^2', '-', 'w_A^2 2 y y_A', '-', 'w_B^2 y^2', '+', 'w_B^2 2 y y_B'),
                   Texx('+ w_A^2 x_A^2', '- w_B^2 x_B^2', '+ w_A^2 y_A^2', '- w_B^2 y_B^2', '= 0')).arrange(DOWN)
        self.play(ReplacementTransform(r, s))
        self.wait(.5)
        t = VGroup(Texx('w_A^2 x^2', '-', 'w_B^2 x^2', '+', 'w_B^2 2 x x_B', '-', 'w_A^2 2 x x_A'),
                   Texx('+ w_A^2 y^2', '-', 'w_B^2 y^2', '+', 'w_B^2 2 y y_B', '-', 'w_A^2 2 y y_A'),
                   Texx('+ w_A^2 x_A^2', '- w_B^2 x_B^2', '+ w_A^2 y_A^2', '- w_B^2 y_B^2', '= 0')).arrange(DOWN)
        self.play(ReplacementTransform(s, t))
        self.wait(.5)
        u1 = VGroup(Texx('(w_A^2 - w_B^2) x^2', '+ 2(w_B^2 x_B - w_A^2 x_A) x'),
                   Texx('+ (w_A^2 - w_B^2) y^2', '+ 2(w_B^2 y_B - w_A^2 y_A) y'),
                   Texx('+ (w_A x_A)^2', '- (w_B x_B)^2', '+ (w_A y_A)^2', '- (w_B y_B)^2', '= 0')).arrange(DOWN)
        self.play(ReplacementTransform(t, u1))
        self.wait(.5)

        v1 = Texx(r"""
\begin{cases}
\end{cases}""").shift(1.5*DOWN)
        comment = Tex('Simplifying expression', color=GRAY).next_to(v1, UP)
        self.play(u1.animate.shift(UP), Write(v1), FadeIn(comment))
        self.wait(.5)

        u2 = VGroup(Texx('a x^2', '+ 2(w_B^2 x_B - w_A^2 x_A) x'),
                   Texx('+ (w_A^2 - w_B^2) y^2', '+ 2(w_B^2 y_B - w_A^2 y_A) y'),
                   Texx('+ (w_A x_A)^2', '- (w_B x_B)^2', '+ (w_A y_A)^2', '- (w_B y_B)^2', '= 0')).arrange(DOWN).shift(UP)
        v2 = Texx(r"""
\begin{cases}
    a = w_A^2 - w_B^2
\end{cases}""").shift(1.5*DOWN)
        self.play(ReplacementTransform(u1, u2),
                  ReplacementTransform(v1, v2),
                  FadeOut(comment))
        u3 = VGroup(Texx('a x^2', '+ b x'),
                   Texx('+ (w_A^2 - w_B^2) y^2', '+ 2(w_B^2 y_B - w_A^2 y_A) y'),
                   Texx('+ (w_A x_A)^2', '- (w_B x_B)^2', '+ (w_A y_A)^2', '- (w_B y_B)^2', '= 0')).arrange(DOWN).shift(UP)
        v3 = Texx(r"""
\begin{cases}
    a = w_A^2 - w_B^2 \\
    b = 2(w_B^2 x_B - w_A^2 x_A)
\end{cases}""", font_size=40).shift(1.2*DOWN)
        self.play(ReplacementTransform(u2, u3), ReplacementTransform(v2, v3))
        u4 = VGroup(Texx('a x^2', '+ b x'),
                   Texx('+ c y^2', '+ 2(w_B^2 y_B - w_A^2 y_A) y'),
                   Texx('+ (w_A x_A)^2', '- (w_B x_B)^2', '+ (w_A y_A)^2', '- (w_B y_B)^2', '= 0')).arrange(DOWN).shift(UP)
        v4 = Texx(r"""
\begin{cases}
    a = w_A^2 - w_B^2 \\
    b = 2(w_B^2 x_B - w_A^2 x_A) \\
    c = w_A^2 - w_B^2
\end{cases}""", font_size=34).shift(1.5*DOWN)
        self.play(ReplacementTransform(u3, u4), ReplacementTransform(v3, v4))
        u5 = VGroup(Texx('a x^2', '+ b x'),
                   Texx('+ c y^2', '+ d y'),
                   Texx('+ (w_A x_A)^2', '- (w_B x_B)^2', '+ (w_A y_A)^2', '- (w_B y_B)^2', '= 0')).arrange(DOWN).shift(UP)
        v5 = Texx(r"""
\begin{cases}
    a = w_A^2 - w_B^2 \\
    b = 2(w_B^2 x_B - w_A^2 x_A) \\
    c = w_A^2 - w_B^2 \\
    d = 2(w_B^2 y_B - w_A^2 y_A)
\end{cases}""", font_size=30).shift(1.5*DOWN)
        self.play(ReplacementTransform(u4, u5), ReplacementTransform(v4, v5))
        u6 = VGroup(Texx('a x^2', '+ b x'),
                   Texx('+ c y^2', '+ d y'),
                   Texx('+ e', '= 0')).arrange(DOWN).shift(UP)
        v6 = Texx(r"""
\begin{cases}
    a = w_A^2 - w_B^2 \\
    b = 2(w_B^2 x_B - w_A^2 x_A) \\
    c = w_A^2 - w_B^2 \\
    d = 2(w_B^2 y_B - w_A^2 y_A) \\
    e = (w_A x_A)^2 - (w_B x_B)^2 + (w_A y_A)^2 - (w_B y_B)^2
\end{cases}""", font_size=26).shift(1.5*DOWN)
        self.play(ReplacementTransform(u5, u6), ReplacementTransform(v5, v6))
        self.wait(.5)
        u7 = Texx('a x^2 + b x', '+', 'a y^2 + d y', '+', 'e = 0').shift(UP)
        self.play(ReplacementTransform(u6, u7))

        self.play(u7.animate.shift(DOWN), FadeOut(v6))
        self.wait(.5)

        u8 = Texx('(a x^2 + b x)', '+', '(a y^2 + d y)', '+', 'e = 0')
        self.play(ReplacementTransform(u7, u8))
        self.wait(.5)
        u9 = Texx(r'(a (x - \frac{b}{2 a})^2', r'- \frac{b^2}{4 a^2})', '+', r'(a (y - \frac{d}{2 a})^2 - \frac{d^2}{4 a^2})', '+', 'e = 0')
        self.play(ReplacementTransform(VGroup(u8, m), u9))
        self.wait(.5)
        u10 = Texx(r'a (x - \frac{b}{2 a})^2', '-', r'\frac{b^2}{4 a^2}', '+', r'a (y - \frac{d}{2 a})^2', '-', r'\frac{d^2}{4 a^2}', '+', 'e = 0')
        self.play(ReplacementTransform(u9, u10))
        self.wait(.5)
        u11 = Texx(r'a (x - \frac{b}{2 a})^2', '+', r'a (y - \frac{d}{2 a})^2', '-', r'\frac{d^2}{4 a^2}', '-', r'\frac{b^2}{4 a^2}', '+', 'e = 0')
        self.play(ReplacementTransform(u10, u11))
        u12 = Texx(r'(x - \frac{b}{2 a})^2', '+', r'(y - \frac{d}{2 a})^2', '-', r'\frac{b^2}{4 a^3}', '-', r'\frac{d^2}{4 a^3}', '+', r'\frac{e}{a} = 0')
        self.play(ReplacementTransform(u11, u12))
        self.wait(.5)

        w1 = Texx(r"""
\begin{cases}
\end{cases}""").shift(1.5*DOWN)
        comment = Tex('Simplifying expression', color=GRAY).next_to(w1, UP)
        self.play(u12.animate.shift(UP), Write(w1), FadeIn(comment))
        self.wait(.5)
        u13 = Texx('(x - x_0)^2', '+', r'(y - \frac{d}{2 a})^2', '-', r'\frac{b^2}{4 a^3}', '-', r'\frac{d^2}{4 a^3}', '+', r'\frac{e}{a} = 0').shift(UP)
        w2 = Texx(r"""
\begin{cases}
    x_0 = \frac{b}{2 a}
\end{cases}""").shift(1.5*DOWN)
        self.play(ReplacementTransform(u12, u13),
                  ReplacementTransform(w1, w2),
                  FadeOut(comment))
        u14 = Texx('(x - x_0)^2', '+', r'(y - y_0)^2', '-', r'\frac{b^2}{4 a^3}', '-', r'\frac{d^2}{4 a^3}', '+', r'\frac{e}{a} = 0').shift(UP)
        w3 = Texx(r"""
\begin{cases}
    x_0 = \frac{b}{2 a} \\
    y_0 = \frac{d}{2 a}
\end{cases}""").shift(1.5*DOWN)
        self.play(ReplacementTransform(u13, u14), ReplacementTransform(w2, w3))
        u15 = Texx('(x - x_0)^2', '+', r'(y - y_0)^2', '+', 'r^2 = 0').shift(UP)
        w4 = Texx(r"""
\begin{cases}
    x_0 = \frac{b}{2 a} \\
    y_0 = \frac{d}{2 a} \\
    r^2 = \frac{e}{a} - \frac{b^2}{4 a^3} - \frac{d^2}{4 a^3}
\end{cases}""").shift(1.5*DOWN)
        self.play(ReplacementTransform(u14, u15), ReplacementTransform(w3, w4))
        self.wait(.5)

        self.play(u15.animate.shift(DOWN), FadeOut(w4))
        circle = Tex('Equation of a circle', color=GRAY).next_to(u15, UP)
        self.play(FadeIn(circle))
        self.wait()

        self.play(FadeOut(title, u15, circle))

    def third_scene(self):
        bounds = get_bounds(self.camera, 1)
        np.random.seed(6)
        cells = [Cell(v2(np.random.uniform(bounds.left+1, bounds.right-1),
                         np.random.uniform(bounds.top+1, bounds.bottom-1)),
                      np.random.uniform()*3+2)
                 for _ in range(50)]
        polygons, dots, _ = make_polygons_and_dots(
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

        edges = VGroup(Polygon(*polygon.points, fill_opacity=0, stroke_color=FG)
                       for polygon in polygons)

        self.play(AnimationGroup(Write(vertices), Write(edges), lag_ratio=.5),
                  rate_func=linear, run_time=5)

        everything = VGroup(polygons, vertices, edges)
        scale = 3
        shift = 2*RIGHT
        # not using FadeOut to avoid the animation being discarded by the group
        self.play(vertices.animate.set_opacity(0))
        self.play(everything.animate.scale(scale).shift(shift))
        self.wait()

        self.play(FadeOut(polygons))
        self.wait()

        vertices.set_opacity(1)
        self.play(Write(vertices))
        self.wait()

        polygons.set_opacity(0)
        self.play(everything.animate.shift(-shift).scale(1/scale))
        self.play(polygons.animate.set_opacity(1), FadeOut(vertices))
        self.wait()

        self.play(FadeOut(polygons, edges))
        self.wait()
