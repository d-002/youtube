from math import tau, cos, sin, atan2
import numpy as np

from manim import *

from fast_voronoi import *
from fast_voronoi.utils import perp_bisector, get_equidistant
from fast_voronoi.neighbors import is_neighbor
from fast_voronoi.intersections import cells_intersections
from fast_voronoi.polygons import make_polygons

from theme import *
from utils import *
from texx import Texx

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        Tex.set_default(color=FG, stroke_color=FG, font_size=32)
        MathTex.set_default(color=FG, stroke_color=FG, font_size=32)
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

    def first_scene(self):
        bounds = get_bounds(self.camera, 1)
        A, B, C = cells = [Cell(v2(-1, 2)), Cell(v2(-2, -3)), Cell(v2(4, 0))]
        polygons, dots, colors = make_polygons_and_dots(
                cells, bounds, THEME3, theme_func_gradient)
        colors = [COL1, COL2, COL3]
        for color, dot in zip(colors, dots):
            dot.set_z_index(1).set_color(color)
        labels = VGroup(Text(text, color=color, stroke_color=color).next_to(dot, UR)
                        for text, color, dot in zip('ABC', colors, dots)).set_z_index(1)

        P = Dot((0, 0, 0), color=COL5).set_z_index(1)
        p_label = Text('P?', color=COL5, stroke_color=COL5).set_z_index(1)
        p_label.add_updater(lambda m: m.next_to(P, UR))

        self.play(FadeIn(dots), Write(labels))
        self.play(Write(P), Write(p_label))
        self.wait()
        self.play(P.animate.move_to((1, -.5, 0)))
        self.play(P.animate.move_to((-2, 1, 0)))
        self.play(P.animate.move_to((-3.5, -1, 0)))
        self.wait()

        ab = perp_bisector(A.pos, B.pos)
        ab_line = Line(*get_ends_from_bisector(bounds, ab), color=FG)
        ac = perp_bisector(A.pos, C.pos)
        ac_line = Line(*get_ends_from_bisector(bounds, ac), color=FG)

        self.play(Write(ab_line))
        self.wait(.5)
        u = ab.M + ab.u
        self.play(P.animate.move_to((u.x, u.y, 0)), run_time=.7)
        u = ab.M - ab.u
        self.play(P.animate.move_to((u.x, u.y, 0)), run_time=.7)
        u = ab.M + ab.u
        self.play(P.animate.move_to((u.x, u.y, 0)), run_time=.7)
        self.wait()

        perp_text = Text('Perpendicular bisector', font_size=36).to_corner(DR)
        self.play(Write(perp_text), run_time=2)
        self.wait()

        self.play(Write(ac_line))
        self.wait(.5)

        inter = get_equidistant(A.pos, B.pos, C.pos)
        self.play(P.animate.move_to((inter.x, inter.y, 0)), run_time=2)

        new_p_label = Text('P', color=COL5, stroke_color=COL5).next_to(P, UR)
        self.play(Transform(p_label, new_p_label))
        self.wait()

        self.play(Unwrite(ab_line), Unwrite(ac_line), Unwrite(dots),
                  Unwrite(labels), Unwrite(P), Unwrite(p_label),
                  Unwrite(perp_text, run_time=.5))
        self.wait()

    def second_scene(self):
        demo1 = Tex(r"""Definitions:

\begin{itemize}
\item Let $S \subset \mathbb{R}^2$ be a finite set of distinct Voronoi sites.

The \textit{common edge} $E \subset \mathbb{R}^2$ between two Voronoi sites $A, B \in S$ is
\[E = \{x \in \mathbb{R}^2, \forall y \in S, \lVert \vec{Ax} \rVert = \lVert \vec{Bx} \rVert \leq \lVert \vec{xy} \rVert \}\]

\item Two Voronoi cells with respective sites $A$, $B$ are said to be \textit{neighbors} if their common edge $E$ is nonempty.
\end{itemize}

Proof:

Let $A, B, C \in \mathbb{R}^2$ be Voronoi sites that are pairwise neighbors.

Let $P \subset \mathbb{R}^2$, the set of intersection points of the three cells, be
\[P = \{x \in \mathbb{R}^2, \lVert \vec{Ax} \rVert = \lVert \vec{Bx} \rVert = \lVert \vec{Cx} \rVert \}\]

Let $d_1$ and $d_2$ be the perpendicular bisectors of $AB$ and $AC$, respectively.

\begin{itemize}
\item Case 1: $A$, $B$ and $C$ are not colinear:
$d_1$ and $d_2$ are not parallel, meaning they have a single intersection point and $\lvert P \rvert = 1$.
\end{itemize}""", font_size=18)

        demo2 = Tex(r"""\begin{itemize}
\item Case 2: $A$, $B$ and $C$ are colinear:

Because these names are interchangeable, we will arrange them so that $A$, $C$ and $B$ are aligned in this order ($\vec{CA} \cdot \vec{CB} < 0$).

Let $H$ be the midpoint between $A$ and $B$, which is therefore both part of $d_1$, and colinear with $A$, $B$ and $C$.

By definition of $C$ strictly (distinct sites) in between $A$ and $B$, $\lVert \vec{HC} \rVert < \lVert \vec{HA} \rVert$.

Let $E$ be the common edge between $A$ and $B$.
If $E$ is nonempty, an element $x$ will be picked from it.

Because $\lVert \vec{xC} \rVert = \sqrt{\lVert \vec{xH} \rVert^2 + \lVert \vec{HC} \rVert^2}$, $\lVert \vec{xA} \rVert = \sqrt{\lVert \vec{xH} \rVert^2 + \lVert \vec{HA} \rVert^2}$ and $\lVert \vec{HC} \rVert < \lVert \vec{HA} \rVert$, it follows that $\lVert \vec{xC} \rVert < \lVert \vec{xA} \rVert$, which contradicts the definition of $E$.

$E$ is therefore empty, which does not correspond to the initial conditions and renders the case impossible.
\end{itemize}

We therefore conclude that the intersection point between $A$, $B$ and $C$, the sites of three neighboring Voronoi cells, if it exists, is unique.
""", font_size=18)
        demo1.shift(3.5*LEFT)
        demo2.shift(3.5*RIGHT)
        self.play(Write(demo1), Write(demo2), run_time=2, lag_ratio=.3)
        self.wait()
        self.play(FadeOut(demo1), FadeOut(demo2))

    def third_scene(self):
        t2c.update({'x_u': COL5, 'y_u': COL5, 'x_v': COL6, 'y_v': COL6, 'u': COL5, 'v': COL6, 'x_M': COL5, 'y_M': COL5, 'x_N': COL6, 'y_N': COL6, 'M': COL5, 'N': COL6})
        Tex.set_default(tex_template=template)

        title = Tex('Getting the equidistant point $P$ between $A$, $B$, $C$', font_size=48).to_edge(UP)
        self.play(FadeIn(title))

        section = Tex('Finding perpendicular bisectors $d_{AB}$ and $d_{AC}$').to_corner(DL)
        self.play(FadeIn(section))
        a = Texx(r'M = \frac{A+B}{2},', 'u = (y_B-y_A, x_A-x_B)')
        b = Texx(r'N = \frac{A+C}{2},', 'v = (y_C-y_A, x_A-x_C)')
        a.next_to(b, UP)
        c = Texx(r'd_{AB} =', 'M + tu').move_to(a)
        d = Texx(r'd_{AC} =', r'N + t^\prime v').move_to(b)
        self.play(AnimationGroup(Write(a), Write(b), lag_ratio=.5))
        self.play(ReplacementTransform(a, c), ReplacementTransform(b, d))
        self.play(c.animate.to_edge(LEFT).shift(UP), d.animate.to_edge(LEFT).shift(UP))

        _section = section
        section = Tex('Finding $t$ in $P = M + t u$').to_corner(DL)

        e = Texx('P', '=', 'd_{AB}', r'\cap', 'd_{AC}')
        self.play(ReplacementTransform(_section, section), Write(e))

        ftext = 'P', '=', 'M + t u', '=', r'N + t^\prime v'
        f = Texx(*ftext)
        self.wait(.5)
        self.play(ReplacementTransform(c, f),
                  ReplacementTransform(d, f),
                  ReplacementTransform(e, f))
        f1 = Texx(*ftext)
        self.add(f1)
        self.play(f1.animate.to_edge(RIGHT).shift(2*UP))

        g = Texx('M + t u', '=', r'N + t^\prime v')
        self.play(TransformMatchingTex(f, g))
        h = Texx('y_M + t y_u', '=', r'y_N + t^\prime y_v')
        self.play(ReplacementTransform(g, h))
        i = Texx(r't^\prime', '= ', r'\frac{y_M - y_N + t y_u}{y_v}')
        self.play(ReplacementTransform(h, i))
        self.play(i.animate.next_to(f1, DOWN))

        f2 = Texx(*ftext).move_to(f1)
        self.add(f2)
        self.play(f2.animate.move_to(ORIGIN))
        k = Texx('M + t u', '=', r'N + t^\prime v')
        self.play(TransformMatchingTex(f2, k))
        p = Texx('x_M + t x_u', '=', r'x_N + t^\prime x_v')
        self.play(ReplacementTransform(k, p))
        p_ = Texx('x_M + t x_u', '= ', 'x_N +', 't^\prime', 'x_v')
        self.add(p_)
        self.remove(p)

        q = Texx('x_M + t x_u', '=', 'x_N +', r'\frac{y_M - y_N + t y_u}{y_v}', 'x_v')
        self.play(TransformMatchingTex(VGroup(i, p_), q))
        r = Texx('x_M + t x_u', '=', 'x_N +', '(y_M - y_N', '+', 't y_u', ')', r'\frac{x_v}{y_v}')
        self.play(ReplacementTransform(q, r))
        s = Texx('x_M + t x_u', '=', 'x_N +', '(y_M - y_N', ')', r'\frac{x_v}{y_v}', '+ t y_u', r'\frac{x_v}{y_v}')
        self.play(TransformMatchingTex(r, s))
        t = Texx(r'x_M - x_N - (y_M - y_N)\frac{x_v}{y_v}', '=', r't y_u\frac{x_v}{y_v} - t x_u')
        self.play(ReplacementTransform(s, t))
        u = Texx(r'x_M - x_N - (y_M - y_N)\frac{x_v}{y_v}', '=', r't (y_u\frac{x_v}{y_v} - x_u)')
        self.play(ReplacementTransform(t, u))
        v = VGroup(Tex('with'), Texx(r't', '=', r'\frac{x_M - x_N - (y_M - y_N)\frac{x_v}{y_v}}{y_u\frac{x_v}{y_v} - x_u}')).arrange(RIGHT, buff=.1)
        self.play(ReplacementTransform(u, v))
        self.play(f1.animate.move_to(ORIGIN), v.animate.shift(DOWN))
        w = Texx('P', '=', 'M + t u')
        self.play(TransformMatchingTex(f1, w))

        self.wait()

    def fourth_scene(self):
        """
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

        self.play(Write(vertices), run_time=2)
        self.wait()
        self.play(Write(edges), run_time=2)
        self.wait()
        self.play(AnimationGroup(FadeOut(polygons), FadeOut(edges), lag_ratio=.5))
        self.wait()
        self.play(FadeOut(vertices))
        self.wait()
        """

        t = ValueTracker(0)
        vec = Vector(color=COL1)

        def create_number():
            pos = vec.get_end()
            angle = round(atan2(pos[1], pos[0])*360) % 360
            return MathTex('%d\deg' % angle, font_size=48).set_color(COL1).next_to(text2)

        text1 = Tex('atan2(', '$y$, $x$', ')', font_size=100).set_color('#FF0000')
        text2 = Tex('atan2(', '$P$', ')', ' =', font_size=48).to_corner(UL)
        result1 = MathTex('0\deg', font_size=48).set_fill(color=COL1, opacity=0).next_to(text1)
        result2 = always_redraw(create_number)

        bg1 = SurroundingRectangle(text1, color=BLACK, fill_opacity=0, stroke_opacity=0).set_z_index(-1)
        bg2 = SurroundingRectangle(VGroup(text2, result2), color=BLACK, fill_opacity=.7).set_z_index(-1)

        self.camera.background_color = "#200000"
        self.add(text1)
        self.add(result1)
        self.wait()

        plane = NumberPlane(**number_plane_config).add_coordinates().set_z_index(-1)
        self.camera.background_color = BG
        self.add(bg1)
        self.play(FadeIn(plane),
                  ReplacementTransform(text1, text2),
                  ReplacementTransform(bg1, bg2),
                  ReplacementTransform(result1, result2))

        radius = .15
        point = Dot(color=COL1, radius=radius).move_to((2, 0, 0))
        vec.put_start_and_end_on(ORIGIN, (2-radius, 0, 0))
        self.play(Write(point), Write(vec))

        def point_updater(m):
            angle = t.get_value()*tau
            pos_norm = np.array([cos(angle), sin(angle), 0])

            m.move_to(pos_norm*2)
            vec.put_start_and_end_on(ORIGIN, pos_norm * (2-radius))

        point.add_updater(point_updater)
        self.play(t.animate.set_value(1), rate_func=smoothstep, run_time=5)
        point.clear_updaters()
        self.wait()

        points = VGroup(Dot((x, y, 0), color=COL1, radius=radius) for x, y in [(2.5, 0), (1.5, 1.5), (-.5, 2), (-2.5, 1), (-1, -2), (1.5, -1.5)]).set_z_index(1)
        self.play(Write(points), Unwrite(point), vec.animate.put_start_and_end_on(ORIGIN, (2.5-radius, 0, 0)))
        self.wait()

        for point in points:
            circle = Circle(radius=.05, color=COL1).move_to(point)
            self.add(circle)
            self.play(circle.animate.scale(10).set_opacity(0), run_time=.5)
            self.remove(circle)
        self.wait()

        def vec_updater(m):
            point = a.get_center() + (b.get_center()-a.get_center())*t.get_value()
            angle = atan2(point[1], point[0])
            r = np.sqrt(np.sum(point**2))

            u = np.array([cos(angle), sin(angle), 0])
            vec.put_start_and_end_on(ORIGIN, u * (r-radius))
            line.put_start_and_end_on(a.get_center(), u*r)

        vec.add_updater(vec_updater)
        for i in range(len(points)):
            a, b = points[i], points[(i+1) % len(points)]
            t.set_value(0)
            line = Line(color=COL1)
            self.add(line)
            self.play(t.animate.set_value(1), rate_func=smoothstep, run_time=.7)
        vec.clear_updaters()
        polygon = Polygon(*[point.get_center() for point in points],
                          stroke_opacity=0, fill_color=COL1, fill_opacity=.5).set_z_index(-1)
        self.play(FadeIn(polygon), Unwrite(vec))
        self.remove(result2)
        self.add(result1)
        self.wait()

    def fifth_scene(self):
        bounds = get_bounds(self.camera, 1)
        top, left, w, h = bounds.top, bounds.left, bounds.w, bounds.h
        bounds = Bounds(left, top*3, w, h*3)
        A, B, C, D = cells = [Cell(v2(-w*.15, 0)), Cell(v2(w*.15, 0)), Cell(v2(0, h*.9)), Cell(v2(0, -h*.9))]
        col1 = lambda t: COL2 + (COL1-COL2)*t
        col2 = COL4

        dots = VGroup(Dot((u.x, u.y, 0), radius=.15, color=FG) for u in [A.pos, B.pos])

        def updater(_):
            y = h*.9 * (1-t.get_value()*.999)
            cells[2].pos.y = y
            cells[3].pos.y = -y

            for i, polygon in make_polygons(options, bounds, cells):
                if i < 2:
                    col = col1(t.get_value())
                else:
                    col = col2

                polygons[i].set_points_as_corners([(u.x, u.y, 0) for u in polygon])
                polygons[i].set_color(col)
                polygons[i].set_stroke(color=FG)

        t = ValueTracker(0)
        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]

        polygons = VGroup(Polygon(*dummy, fill_opacity=.5) for _ in range(4))
        updater(None)
        self.play(FadeIn(polygons), Write(dots))
        polygons.add_updater(updater)

        self.play(t.animate.set_value(1), run_time=4)
        polygons.clear_updaters()

        self.play(FadeOut(polygons), FadeOut(dots), run_time=.5)
        self.wait()
