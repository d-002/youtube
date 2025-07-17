from manim import *

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG
