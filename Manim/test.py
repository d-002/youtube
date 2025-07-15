from manim import *

class Test(Scene):
    def construct(self):
        text = Text("Hello world", color=RED)
        text.set_stroke(RED)
        self.play(Write(text))
        self.wait(1)
        self.play(Unwrite(text))
