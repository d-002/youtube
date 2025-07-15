from manim import *

from theme import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG)
        self.camera.background_color = BG
