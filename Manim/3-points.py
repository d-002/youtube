from manim import *

from fast_voronoi import *
from fast_voronoi.utils import perp_bisector, get_equidistant

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        Tex.set_default(color=FG, stroke_color=FG, font_size=32)
        MathTex.set_default(color=FG, stroke_color=FG, font_size=32)
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
        # config
        template = TexTemplate(preamble=r"\usepackage{xcolor}")
        t2c1 = {'A': COL1, 'B': COL2, 'C': COL3, 'P': COL4}
        t2c2 = {**t2c1, 'u': COL5, 'v': COL6, 'M': COL5, 'N': COL6}
        texcolors = {}
        name_ord = 65
        for col in t2c2.values():
            name = chr(name_ord)
            name_ord += 1
            template.add_to_preamble(r'\definecolor{'+name+'}{HTML}{'+col.to_hex()[1:]+'}')
            texcolors[col] = name
        Tex.set_default(tex_template=template)

        def col(*args):
            strings, pairs = args[:-1], args[-1]

            dst = []
            for s in strings:
                final = ''
                for c in s:
                    found = False
                    for c2, col in pairs.items():
                        if c == c2:
                            # add spaces to prevent double braces
                            final += r' {\textcolor{'+texcolors[col]+'}{'+c+'} } '
                            found = True
                            break

                    if not found:
                        final += c

                dst.append(final)

            return dst

        title = Tex(*col(r'Getting the equidistant point $P$ between $A$, $B$, $C$', t2c1), font_size=48).to_edge(UP)
        self.play(FadeIn(title), run_time=1.5)
        self.wait(.5)

        section = Tex(*col('Finding perpendicular bisectors $d_{AB}$ and $d_{AC}$', t2c1)).to_corner(DL)
        self.play(FadeIn(section))
        a = Tex(*col(r'$M = \frac{A+B}{2},$', '$u = (y_B-y_A, x_A-x_B)$', t2c2))
        b = Tex(*col(r'$N = \frac{A+C}{2},$', '$v = (y_C-y_A, x_A-x_C)$', t2c2))
        a.next_to(b, UP)
        c = Tex(*col(r'$d_{AB} =$', '$M + tu$', t2c2)).move_to(a)
        d = Tex(*col(r'$d_{AC} =$', r'$N + t^\prime v$', t2c2)).move_to(b)
        self.play(AnimationGroup(Write(a), Write(b), lag_ratio=.5))
        self.play(ReplacementTransform(a, c), ReplacementTransform(b, d))
        self.play(c.animate.to_edge(LEFT).shift(UP), d.animate.to_edge(LEFT).shift(UP))

        _section = section
        section = Tex('Finding $t$ in $P = M + t u$').to_corner(DL)

        e = Tex(*col('$P$', '$=$', '$d_{AB}$', r'$\cap$', '$d_{AC}$', t2c2))
        self.play(ReplacementTransform(_section, section), Write(e))

        ftext = col('$P$', '$=$', '$M + t u$', '$=$', r'$N + t^\prime v$', t2c2)
        f = Tex(*ftext)
        self.wait(.5)
        self.play(ReplacementTransform(c, f),
                  ReplacementTransform(d, f),
                  ReplacementTransform(e, f))
        f1 = Tex(*ftext)
        self.add(f1)
        self.play(f1.animate.to_edge(RIGHT).shift(2*UP))

        g = Tex(*col('$M + t u$', '$=$', r'$N + t^\prime v$', t2c2))
        self.play(TransformMatchingTex(f, g))
        h = Tex(*col('$y_M + t y_u$', '$=$', r'$y_N + t^\prime y_v$', t2c2))
        self.play(ReplacementTransform(g, h))
        i = Tex(*col(r'$t^\prime$', '$= $', r'$\frac{y_M - y_N + t y_u}{y_v}$', t2c2))
        self.play(ReplacementTransform(h, i))
        self.play(i.animate.next_to(f1, DOWN))
        return

        f2 = MathTex(*ftext).move_to(f1)
        self.play(f2.animate.move_to(ORIGIN))
        f3 = MathTex(*ftext)
        self.add(f3)
        k = MathTex('P', '=', 'M + t u')
        l = MathTex('P', '=', r'N + t^\prime v').shift(DOWN)
        self.play(TransformMatchingTex(f2, k),
                  TransformMatchingTex(f3, l))

        m = MathTex('x_P', '=', 'x_M + t x_u')
        n = MathTex('x_P', '=', r'x_N + t^\prime x_v').move_to(l)
        self.play(ReplacementTransform(k, m),
                  ReplacementTransform(l, n))

        p = MathTex('x_M + t x_u', '=', r'x_N + t^\prime x_v')
        self.play(TransformMatchingTex(VGroup(m, n), p))
        p_ = MathTex('x_M + t x_u', '= ', 'x_N +', 't^\prime', 'x_v')
        self.add(p_)
        self.remove(p)

        q = MathTex('x_M + t x_u', '=', 'x_N +', r'\frac{y_M - y_N + t y_u}{y_v}', 'x_v')
        self.play(TransformMatchingTex(VGroup(i, p_), q))
        r = MathTex('x_M + t x_u', '=', 'x_N +', '(y_M - y_N', '+', 't y_u', ')', r'\frac{x_v}{y_v}')
        self.play(ReplacementTransform(q, r))
        s = MathTex('x_M + t x_u', '=', 'x_N +', '(y_M - y_N', ')', r'\frac{x_v}{y_v}', '+ t y_u', r'\frac{x_v}{y_v}')
        self.play(TransformMatchingTex(r, s))
        t = MathTex(r'x_M - x_N - (y_M - y_N)\frac{x_v}{y_v}', '=', r't y_u\frac{x_v}{y_v} - t x_u')
        self.play(ReplacementTransform(s, t))
        u = MathTex(r'x_M - x_N - (y_M - y_N)\frac{x_v}{y_v}', '=', r't (y_u\frac{x_v}{y_v} - x_u)')
        self.play(ReplacementTransform(t, u))
        v = MathTex(r'\text{with } t', '=', r'\frac{x_M - x_N - (y_M - y_N)\frac{x_v}{y_v}}{y_u\frac{x_v}{y_v} - x_u}')
        self.play(ReplacementTransform(u, v))
        self.play(f1.animate.move_to(ORIGIN), v.animate.shift(DOWN))
        w = MathTex('P', '=', 'M + t u')
        self.play(TransformMatchingTex(f1, w))

        self.wait()
