from manim import *
from numpy.random import uniform

from fast_voronoi import *
from fast_voronoi.neighbors import is_neighbor
from fast_voronoi.intersections import cells_intersections

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
        polygons, dots, colors = make_polygons_and_dots(
                cells, bounds, THEME1, theme_func_gradient)

        for polygon in polygons:
            polygon.set_stroke(opacity=0)

        neighbors = [[] for _ in range(len(cells))]
        for i in range(len(cells)):
            for j in range(len(cells)):
                if i == j:
                    continue

            if is_neighbor(bounds, cells, i, j):
                neighbors[i].append(j)

        vertices = cells_intersections(bounds, cells, neighbors)
        print(vertices)
        sdkjhsdkjfh
        vertices = VGroup(Dot((u.x, u.y, 0), color=WHITE) for u in vertices)

        self.play(FadeIn(polygons), Create(dots, lag_ratio=.02))
        self.wait()

        self.play(Write(vertices))
        #self.play(Write(edges))
        self.wait()
