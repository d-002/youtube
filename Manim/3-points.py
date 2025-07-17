from manim import *

from fast_voronoi import *
from fast_voronoi.utils import perp_bisector, get_equidistant

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        #self.first_scene()
        #self.second_scene()
        self.third_scene()

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
        demo1 = Tex("""Definitions:

\\begin{itemize}
\\item Let $S \\subset \\mathbb{R}^2$ be a finite set of distinct Voronoi sites.

The \\textit{common edge} $E \\subset \\mathbb{R}^2$ between two Voronoi sites $A, B \\in S$ is
\\[E = \\{x \\in \\mathbb{R}^2, \\forall y \\in S, \\lVert \\vec{Ax} \\rVert = \\lVert \\vec{Bx} \\rVert \\leq \\lVert \\vec{xy} \\rVert \\}\\]

\\item Two Voronoi cells with respective sites $A$, $B$ are said to be \\textit{neighbors} if their common edge $E$ is nonempty.
\\end{itemize}

Proof:

Let $A, B, C \\in \\mathbb{R}^2$ be Voronoi sites that are pairwise neighbors.

Let $P \\subset \\mathbb{R}^2$, the set of intersection points of the three cells, be
\\[P = \\{x \\in \\mathbb{R}^2, \\lVert \\vec{Ax} \\rVert = \\lVert \\vec{Bx} \\rVert = \\lVert \\vec{Cx} \\rVert \\}\\]

Let $d_1$ and $d_2$ be the perpendicular bisectors of $AB$ and $AC$, respectively.

\\begin{itemize}
\\item Case 1: $A$, $B$ and $C$ are not colinear:
$d_1$ and $d_2$ are not parallel, meaning they have a single intersection point and $\\lvert P \\rvert = 1$.
\\end{itemize}""", font_size=18)

        demo2 = Tex("""\\begin{itemize}
\\item Case 2: $A$, $B$ and $C$ are colinear:

Because these names are interchangeable, we will arrange them so that $A$, $C$ and $B$ are aligned in this order ($\\vec{CA} \\cdot \\vec{CB} < 0$).

Let $H$ be the midpoint between $A$ and $B$, which is therefore both part of $d_1$, and colinear with $A$, $B$ and $C$.

By definition of $C$ strictly (distinct sites) in between $A$ and $B$, $\\lVert \\vec{HC} \\rVert < \\lVert \\vec{HA} \\rVert$.

Let $E$ be the common edge between $A$ and $B$.
If $E$ is nonempty, an element $x$ will be picked from it.

Because $\\lVert \\vec{xC} \\rVert = \\sqrt{\\lVert \\vec{xH} \\rVert^2 + \\lVert \\vec{HC} \\rVert^2}$, $\\lVert \\vec{xA} \\rVert = \\sqrt{\\lVert \\vec{xH} \\rVert^2 + \\lVert \\vec{HA} \\rVert^2}$ and $\\lVert \\vec{HC} \\rVert < \\lVert \\vec{HA} \\rVert$, it follows that $\\lVert \\vec{xC} \\rVert < \\lVert \\vec{xA} \\rVert$, which contradicts the definition of $E$.

$E$ is therefore empty, which does not correspond to the initial conditions and renders the case impossible.
\\end{itemize}

We therefore conclude that the intersection point between $A$, $B$ and $C$, the sites of three neighboring Voronoi cells, if it exists, is unique.
""", font_size=18)
        demo1.shift(3.5*LEFT)
        demo2.shift(3.5*RIGHT)
        self.play(Write(demo1), Write(demo2), run_time=2, lag_ratio=.3)
        self.wait()
        self.play(FadeOut(demo1), FadeOut(demo2))

    def third_scene(self):
        pass
