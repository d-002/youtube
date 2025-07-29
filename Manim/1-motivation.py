from random import randint
from math import cos, sin, pi, tau
from manim import *

from fast_voronoi import *

from theme import *
from utils import *

PRODUCTION = True

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        cells = [Cell(v2(-1, -2), 1), Cell(v2(4, 0), 1), Cell(v2(2, 2), 1)]

        self.first_scene()
        rest = self.second_scene(cells)
        self.third_scene(cells, *rest)

        self.clear()
        self.end_scene()

    def first_scene(self):
        svg = SVGMobject('resources/voronoy.svg').scale(2.85).shift(.3*UP)
        img = ImageMobject('resources/voronoy.png').scale(.625).shift(.3*UP)
        alt = Text('Georgy Feodosevich Voronyi', font_size=20).next_to(img, DOWN)

        example = SVGMobject('resources/diagram_example.svg').shift(20*RIGHT).scale(3)

        self.play(Write(alt))
        self.play(Create(svg), run_time=5, rate_func=linear)
        self.play(
            FadeIn(img),
            # can't use group here
            map(lambda m: m.animate.shift(4*LEFT), (svg, img, alt)),
            example.animate.shift(17*LEFT), run_time=2)
        self.wait()

        self.play(map(
            lambda m: m.animate.shift(10*UP), (svg, img, alt, example)),
                  run_time=2)
        self.remove(svg, img, alt, example)

    def second_scene(self, cells):
        bounds = get_bounds(self.camera, 1)
        colors = [COL1, COL2, COL3]
        polygons, dots = make_polygons_and_dots(cells, bounds, colors)
        polygons.set_z_index(-2)

        self.play(FadeIn(polygons))
        self.wait()
        self.play(Write(dots))
        self.wait()
        self.play(FadeOut(polygons))

        return dots, polygons

    def third_scene(self, cells, dots, polygons):
        bounds = get_bounds(self.camera, 0)
        around = Square(6).set_stroke(GRAY, width=1)
        res = 30
        res2 = res//2
        # warning: column first
        screen = VGroup(Square(.2).move_to((x*.2-2.9, y*.2-2.9, 0)).set_stroke(GRAY_D, width=1)
                        for x in range(res) for y in range(res)).set_z_index(-1)
        colors = [COL1, COL2, COL3]

        if PRODUCTION:
            self.play(Write(around).set_run_time(3), Write(screen).set_run_time(2))
        else:
            self.add(screen, around)
        self.wait()

        rand_colors = [ManimColor.from_rgb((randint(0, 255),)*3) for i in range(900)]
        if PRODUCTION:
            self.play(AnimationGroup(
                (Succession(ApplyMethod(rect.set_fill, color, 1),
                            ApplyMethod(rect.set_fill, color, 0))
                 for color, rect in zip(rand_colors, screen)),
                lag_ratio=.001))
        self.wait()

        circles = VGroup(
                Circle(radius=.05, color=color, fill_opacity=1)
                .move_to((cell.pos.x, cell.pos.y, 0))
                for cell, color in zip(cells, colors))

        self.play(AnimationGroup(
            (dots[i].animate.set_color(colors[i]) for i in range(3)),
            lag_ratio=.2))
        self.add(circles)
        self.play(AnimationGroup(
            (circle.animate.set_opacity(0).scale(20) for circle in circles),
            lag_ratio=.2))
        self.wait()

        centers = [dot.get_center() for dot in dots]
        closest_center_i = lambda pos, centers: \
                min(enumerate(centers), key=lambda arg: np.sum((arg[1]-pos)**2))[0]

        def line_updater(_):
            start = cursor.get_center()
            target = centers[closest_center_i(start, centers)]

            line.put_start_and_end_on(start, target)

        def get_cursor_pos(t):
            a = pi*.5 - t*tau
            c = 2*cos(a)
            s = sin(2*a)
            offset = t*.1
            return (c+s - offset, s-c - offset, 0)

        # must be a lambda, easier scope stuff
        t = ValueTracker(0)
        cursor_updater = lambda _: cursor.move_to(get_cursor_pos(t.get_value()))

        cursor = Dot(color=COL4, radius=.2).move_to(8*LEFT)
        self.add(cursor)
        self.play(cursor.animate.move_to(ORIGIN))
        line = Line(color=COL4).add_updater(line_updater)
        line_updater(line)
        self.play(Create(line))
        self.wait()

        cursor.add_updater(cursor_updater)
        self.play(t.animate.set_value(1), run_time=5, rate_func=smoothstep)
        cursor.clear_updaters()
        line.clear_updaters()

        self.play(Unwrite(cursor))

        self.play(line.animate.set_color(COL1))
        pixel = screen[(res2-1)*res+(res2-1)]
        pixel.set_fill(color=COL1, opacity=0)
        self.play(AnimationGroup(
            Uncreate(line),
            pixel.animate.set_fill(color=COL1, opacity=1),
            lag_ratio=.3))

        self.wait()
        pixels = [[] for _ in range(len(cells))]
        for i, rect in enumerate(screen):
            pos = rect.get_center()
            cindex = closest_center_i(pos, centers)
            rect.set_fill(color=colors[cindex])
            pixels[cindex].append(rect)

        if PRODUCTION:
            self.play(AnimationGroup(
                (rect.animate.set_fill(opacity=.5) for rect in screen),
                lag_ratio=.001, run_time=2))
        else:
            for rect in screen:
                rect.set_fill(opacity=.5)
        self.wait()

        if PRODUCTION:
            self.play(AnimationGroup(
                (AnimationGroup((Succession(ApplyMethod(rect.set_fill, color, 1),
                                            ApplyMethod(rect.set_fill, color, .5))
                                 for rect in group),
                                lag_ratio=.001)
                 for color, group in zip(colors, pixels)),
                lag_ratio=.5))

        if PRODUCTION:
            self.play(AnimationGroup(
                (rect.animate.set_fill(opacity=0) for rect in screen),
                lag_ratio=.001))
        else:
            for rect in screen:
                rect.set_fill(opacity=0)

        for n in range(5):
            rect = screen[randint(0, res*res-1)]
            pos = rect.get_center()
            lines = VGroup(Line(pos, dot.get_center(), color=COL4) for dot in dots)
            self.play(Create(lines, lag_ratio=.5), run_time=.5)

            i = closest_center_i(pos, centers)
            self.play((line.animate.set_stroke(
                **({'color': FG} if i == j else {'opacity': 0}))
                       for j, line in enumerate(lines)), run_time=.5)

            self.play(lines[i].animate.set_stroke(color=colors[i], opacity=0),
                      Uncreate(lines[i]),
                      rect.animate.set_fill(opacity=.5),
                      lag_ratio=.3,
                      run_time=.8)
            self.wait(.2)

        self.wait()
        self.play(FadeOut(screen))
        for polygon in polygons:
            polygon.set_fill(opacity=0)
        self.play(FadeIn(polygons))
        self.play((polygon.animate.set_fill(opacity=1) for polygon in polygons),
                  run_time=3)
        self.wait()

    def end_scene(self):
        cells = [Cell(v2(-1, -2), 1), Cell(v2(4, 0), 1), Cell(v2(2, 2), 1)]
        bounds = get_bounds(self.camera, 0)
        colors = [COL1, COL2, COL3]
        polygons, dots = make_polygons_and_dots(cells, bounds, colors)

        self.play(AnimationGroup(FadeIn(polygons), Write(dots)), lag_ratio=.5)
        self.wait()
        self.play(polygons[1].animate.set_fill(opacity=.1),
                  polygons[2].animate.set_fill(opacity=.1))
        text = Text('All closer to the red site', font_size=24).to_corner(DL)
        self.play(Write(text), run_time=2)
        self.wait()
        self.play(polygons[1].animate.set_fill(opacity=1),
                  polygons[2].animate.set_fill(opacity=1))
        self.wait()

        self.play(FadeOut(text, polygons, dots), run_time=2)
        self.wait()
