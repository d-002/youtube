import numpy as np

from manim import *

from fast_voronoi import *

from theme import *
from utils import *

class Main(Scene):
    def construct(self):
        np.random.seed(0)
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        bounds = get_bounds(self.camera, 1)
        left, top, w, h = bounds.left, bounds.top, bounds.w, bounds.h

        regions = [Cell(v2(-.25*w, .4*h), 1), Cell(v2(-.05*w, -.1*h), 2.5),
                   Cell(v2(.1*w, -.05*h), 3.5), Cell(v2(.25*w, -.5*h), 1.4)]

        bg = Rectangle(width=w, height=h).set_stroke(width=0)
        bg.set_fill(color=[[.23, .26, .61], [.77, .49, .33]], opacity=1)

        colors = [BG]*len(regions)
        strong_edges = make_polygons_and_dots(regions, bounds, colors)[0]

        cells = [Cell(v2(np.random.uniform(left, left+w),
                         np.random.uniform(top, top+h)))
                 for _ in range(50)]

        colors = [BG]*len(cells)
        light_edges = make_polygons_and_dots(cells, bounds, colors)[0]

        for polygon in strong_edges:
            polygon.set_fill(opacity=0).set_stroke(width=20)
        for polygon in light_edges:
            polygon.set_fill(opacity=0).set_stroke(opacity=.2)

        text = VGroup(
                Text('The beauty of', weight=BOLD),
                Text('Voronoi Diagrams', weight=BOLD))
        text.arrange(DOWN).to_edge(UP).shift(1.5*UP)

        self.add(bg)
        self.add(light_edges)
        self.add(strong_edges)
        self.add(text)
        self.wait()
