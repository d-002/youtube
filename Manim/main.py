from manim import *
from fast_voronoi import *
from fast_voronoi.polygons import make_polygons


class VoronoiAnim:
    def __init__(self, options: Options, bounds: Bounds, cells: list[Cell],
                 colors: list[tuple], style_funcs, show_dots: bool = False,
                 buffer: int = 10):
        self.options = options
        self.bounds = bounds
        self.cells = cells
        self.colors = colors

        self.style_polygon, self.style_dot = style_funcs

        # could be a varying number of polygons per cell, so add a small buffer
        length = len(cells)+buffer
        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        self.polygons = VGroup(Polygon(*dummy) for _ in range(length))

        if show_dots:
            self.dots = VGroup(*(Dot((cell.pos.x, cell.pos.y, 0),
                                     radius=.2)
                                       for cell in cells))
        else:
            self.dots = VGroup()

        self.update()

    def update(self):
        polygons = make_polygons(self.options, self.bounds, self.cells)

        index = 0
        for i, points_raw in polygons:
            dots = [(u.x, u.y, 0) for u in points_raw]

            if index >= len(self.polygons):
                raise ValueError('Not enough polygons in VoronoiAnim buffer')
            polygon = self.polygons[index]

            polygon.set_points_as_corners(dots)
            polygon.set_opacity(1) # fallback
            point = self.dots[i]
            self.style_polygon(polygon, self.colors[i])

            index += 1

        # hide the unused polygons
        for i in range(index, len(self.polygons)):
            self.polygons[i].set_opacity(0)

        for i, dot in enumerate(self.dots):
            self.style_dot(dot, self.colors[i])
            u = self.cells[i].pos
            dot.move_to((u.x, u.y, 0))

    def play(self, scene: Scene, func, **kwargs):
        def updater(_):
            func(self, t.get_value())
            self.update()

        t = ValueTracker(0)
        self.polygons.add_updater(updater)
        scene.play(t.animate.set_value(1), **kwargs)
        self.polygons.clear_updaters()


class Dance:
    def __init__(self, camera):
        cx, cy = camera.frame_center[:2]
        w, h = camera.frame_width, camera.frame_height
        x, y = cx-w/2, cy-h/2
        x, y, w, h = x-1, y-1, w+2, h+2

        self.bounds = Bounds(x, y, w, h)

    def init1(self, voronoi):
        voronoi.cells[0].pos = v2(self.bounds.right, 0)

        for i in range(1, len(voronoi.cells)):
            cell = voronoi.cells[i]
            cell.weight = 100
            cell.pos = self.bounds.tl*.5

    def arrive1(self, voronoi, t):
        black = voronoi.cells[0]
        black.pos.x = (1-t)*self.bounds.right


class Main(Scene):
    def construct(self):
        def style_poly_transparent(polygon: Polygon, color: tuple):
            polygon.set_stroke(color)
            polygon.set_fill(color, opacity=.5)

        def style_poly_fill(polygon: Polygon, color: tuple):
            polygon.set_stroke(width=0)
            polygon.set_fill(color, opacity=1)

        def style_dot(dot: Dot, color: ManimColor):
            r, g, b = color.to_rgb()
            r, g, b = int(r*255), int(g*255), int(b*255)
            dot.set_color(ManimColor.from_rgb((255-r, 255-g, 255-b)))

        """
        text = Text('Headphones recommended',
                    font_size=20)
        self.play(Write(text, run_time=2))
        self.wait(1)
        self.play(FadeOut(text, run_time=5))
        """

        dance = Dance(self.camera)
        bounds = dance.bounds

        options = Options(segments_density=10, divide_lines=True)
        cells = [Cell(v2(-2, 0), 1), Cell(v2(2, 0), 2)]
        colors = [BLACK, WHITE]

        funcs = style_poly_fill, style_dot
        voronoi = VoronoiAnim(options, bounds, cells, colors, funcs, True)

        self.add(voronoi.polygons)
        self.add(voronoi.dots)
        dance.init1(voronoi)
        voronoi.update()
        voronoi.play(self, dance.arrive1, run_time=2)
