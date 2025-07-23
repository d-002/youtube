from manim import *

from theme import *
from utils import *

import numpy as np

from fast_voronoi import *

class Main(Scene):
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

    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        """
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
        """

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

        options = Options(segments_density=10, divide_lines=True, complete_polygons=True)
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
