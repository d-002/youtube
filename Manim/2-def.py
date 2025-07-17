from manim import *
from numpy.random import uniform

from fast_voronoi import *

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG)
        self.camera.background_color = BG

        bounds = get_bounds(self.camera, 0)
        cells = [Cell(v2(uniform(bounds.left+1, bounds.right-1),
                         uniform(bounds.top+1, bounds.bottom-1)))
                 for _ in range(50)]
        colors = [THEME2[i%len(THEME2)] for i in range(len(cells))]
        polygons, dots = make_polygons_and_dots(cells, bounds, colors)

        self.add(polygons, dots)
        self.wait()
