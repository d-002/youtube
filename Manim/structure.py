from manim import *

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        titles = [
                'A motivation',
                'Points in space',
                'Neighborhood complications',
                'Thinking outside the circle',
                'Exercising with weights',
                'Closing thoughts']

        for i, text in enumerate(titles):
            title = Text(f'Chapter {i}:', font_size=64, font='URW Gothic')
            subtitle = Text(text, font_size=36)
            title.shift(.5*UP)
            subtitle.next_to(title, DOWN)

            self.play(Create(title), run_time=.5)
            self.wait(.8)
            self.play(Write(subtitle))
            self.wait()
            self.play(FadeOut(title, subtitle))
            self.wait()
