from manim import *

from theme import *

class Main(Scene):
    def construct(self):
        img = SVGMobject("resources/voronoy.svg").scale(4)
        self.play(Create(img), run_time=5, rate_func=linear)
