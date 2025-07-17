from manim import *

from fast_voronoi import *
from fast_voronoi.utils import perp_bisector, get_equidistant

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

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
