from manim import *
from fast_voronoi import *
from fast_voronoi.polygons import make_polygons

#from manim import config
#config.transparent = True

class VoronoiAnim:
    def __init__(self, options: Options, bounds: Bounds, cells: list[Cell],
                 colors: list[tuple], style_func, buffer: int = 10):
        self.options = options
        self.bounds = bounds
        self.cells = cells
        self.colors = colors

        self.style_func = style_func

        # could be a varying number of polygons per cell, so add a small buffer
        length = len(cells)+buffer
        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        self.vgroup = VGroup(Polygon(*dummy) for _ in range(length))
        self._set_points()

    def _set_points(self):
        polygons = make_polygons(self.options, self.bounds, self.cells)

        index = 0
        for i, points_raw in polygons:
            points = [(u.x, u.y, 0) for u in points_raw]

            if index >= len(self.vgroup):
                raise ValueError('Not enough polygons in VoronoiAnim buffer')
            polygon = self.vgroup[index]

            polygon.set_points_as_corners(points)
            polygon.set_opacity(1) # fallback
            self.style_func(polygon, self.colors[i])

            index += 1

        # hide the unused polygons
        for i in range(index, len(self.vgroup)):
            self.vgroup[i].set_opacity(0)

    def play(self, scene: Scene, func, **kwargs):
        def updater(_):
            func(self, t.get_value())
            self._set_points()

        t = ValueTracker(0)
        self.vgroup.add_updater(updater)
        scene.play(t.animate.set_value(1), **kwargs)
        self.vgroup.clear_updaters()

def bounds_from_camera(camera: Camera) -> Bounds:
    cx, cy = camera.frame_center[:2]
    w, h = camera.frame_width, camera.frame_height
    bounds = Bounds(cx-w/2, cy-h/2, w, h)
    return bounds

class Main(Scene):
    def construct(self):
        def style_poly_transparent(polygon: Polygon, color: tuple):
            polygon.set_stroke(color)
            polygon.set_fill(color, opacity=.5)

        def style_poly_fill(polygon: Polygon, color: tuple):
            polygon.set_stroke(width=0)
            polygon.set_fill(color, opacity=1)

        def updater_swap_weights(voronoi, t):
            c1, c2 = voronoi.cells
            c1.weight = 1+t
            c2.weight = 2-t

        self.camera.background_color = WHITE

        options = Options(segments_density=10, divide_lines=True)
        bounds = bounds_from_camera(self.camera)
        cells = [Cell(v2(-2, 0), 1), Cell(v2(2, 0), 2)]
        colors = [RED, BLUE_E]

        voronoi = VoronoiAnim(options, bounds, cells, colors, style_poly_fill)

        self.add(voronoi.vgroup)
        voronoi.play(self, updater_swap_weights, run_time=3)
