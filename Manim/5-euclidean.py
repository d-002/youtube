from manim import *

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        #self.first_scene()
        self.clear()
        self.second_scene()

    def first_scene(self):
        svg = SVGMobject('resources/pythagoras.svg').scale(2.5)
        img = ImageMobject('resources/pythagoras.jpg')

        self.play(Create(svg).set_run_time(3).set_rate_func(linear))
        self.play(FadeIn(img),
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

        self.play(Write(triangle))
        self.wait()

        tex = VGroup(MathTex('c^2', font_size=48, color=COL3),
                     MathTex('=', font_size=48, color=FG),
                     MathTex('a^2', font_size=48, color=COL1),
                     MathTex('+', font_size=48, color=FG),
                     MathTex('b^2', font_size=48, color=COL2))
        tex.arrange(RIGHT, buff=.2).move_to(triangle, DOWN).shift(DOWN)
        self.play(Write(tex[0]))
        self.wait()
        self.play(Write(tex[1:]), run_time=2)

        self.play(svg.animate.shift(10*LEFT),
                  img.animate.shift(10*LEFT),
                  triangle.animate.shift(8*RIGHT),
                  tex.animate.shift(6*RIGHT))
        self.wait()

    def second_scene(self):
        A, B = Dot((-2, -1, 0), radius=.15, color=FG), Dot((2, 2, 0), radius=.15, color=FG)
        self.play(Write(A), Write(B))
