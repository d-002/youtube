from manim import *

from theme import *
from utils import *

from fast_voronoi import *
from fast_voronoi.polygons import make_polygons

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG)
        self.camera.background_color = BG

        cells = [Cell(-1, -2), Cell(4, 1), Cell(2, 3)]

        #self.first_scene()
        rest = self.second_scene(cells)
        self.third_scene(cells, *rest)

    def first_scene(self):
        svg = SVGMobject("resources/voronoy.svg").scale(2.5).shift(.3*UP)
        img = ImageMobject("resources/voronoy.png").scale(2.5/4).shift(.3*UP)
        voronoy = Text("Georgy Feodosevich Voronyi", font_size=20, stroke_color=FG).next_to(img, DOWN)

        example = SVGMobject("resources/diagram_example.svg").shift(20*RIGHT).scale(3)

        self.play(
            Succession(Wait(1), Create(svg).set_run_time(5).set_rate_func(linear)),
            Write(voronoy.set_run_time(1))
        )
        self.play(
            FadeIn(img),
            # can't use group here
            map(lambda m: m.animate.shift(4*LEFT), (svg, img, voronoy)),
            example.animate.shift(17*LEFT), run_time=2)
        self.wait(1)

        self.play(map(lambda m: m.animate.shift(10*UP), (svg, img, voronoy, example)), run_time=2)
        self.remove(svg, img, voronoy, example)

    def second_scene(self, cells):
        bounds = utils.get_bounds(self.camera)
        print(bounds, utils.options)
        polygons = make_polygons(utils.options, bounds, cells)
        polygons = VGroup(Polygon((u.x, u.y, 0) for u in points) for points in polygons)

        self.play(FadeIn(polygons))
        self.wait(1)

    def third_scene(self, cells, *args):
        pass

