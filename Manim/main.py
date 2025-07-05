from math import pi, cos, sin
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
        black, white = voronoi.cells[:2]
        black.pos = v2(self.bounds.right, 0)
        white.pos = v2(self.bounds.left, 0)
        black.weight = 1
        white.weight = 100

        for i in range(2, len(voronoi.cells)):
            cell = voronoi.cells[i]
            cell.weight = 100
            cell.pos = v2(self.bounds.left, i)

    def arrive1(self, voronoi, t):
        black = voronoi.cells[0]
        black.pos.x = (1-t) * self.bounds.right

    def arrive2(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = t * (.2*self.bounds.right)
        white.pos.x = (1-t*.8) * self.bounds.left

        dist = abs(black.pos.x-white.pos.x)
        white.weight = 5*dist

    def grow(self, voronoi, t):
        white = voronoi.cells[1]
        white.weight = (1-t) * (3*0.4*self.bounds.w - 1) + 1

        light = int(max(0, 2 - t*2)*255)
        dot = voronoi.dots[1]
        dot.set_color(ManimColor.from_rgb((light, light, light)))

    def close(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = (t*.1 + .2)*self.bounds.right
        white.pos.x = (1-t) * (.2*self.bounds.left)

    def updown(self, voronoi, t):
        white = voronoi.cells[1]
        white.pos.y = t * (.2*self.bounds.bottom)

    def rotate(self, voronoi, t):
        black, white = voronoi.cells[:2]

        a1 = (3*pi) * max(0, t*1.05 - .05) # black (lag)
        a2 = 3*pi*t + pi # white
        radius = .2*self.bounds.right

        black.pos = v2(cos(a1), -sin(a1))*radius
        white.pos = v2(cos(a2), -sin(a2))*radius


class Main(Scene):
    def construct(self):
        def style_poly_transparent(polygon: Polygon, color: tuple):
            polygon.set_stroke(color)
            polygon.set_fill(color, opacity=.5)

        def style_poly_fill(polygon: Polygon, color: tuple):
            polygon.set_stroke(width=0)
            polygon.set_fill(color, opacity=1)

        def style_dot_white(dot: Dot, color: ManimColor):
            dot.set_color(WHITE)

        def style_dot_none(dot: Dot, color: ManimColor):
            pass

        def style_dot_invert(dot: Dot, color: ManimColor):
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

        funcs = style_poly_fill, style_dot_white
        voronoi = VoronoiAnim(options, bounds, cells, colors, funcs, True)

        self.add(voronoi.polygons)
        self.add(voronoi.dots)
        dance.init1(voronoi)
        voronoi.update()

        voronoi.play(self, dance.arrive1, run_time=2, rate_func=rush_from)
        self.wait(1.2)

        voronoi.play(self, dance.arrive2, run_time=2)
        self.wait(.8)

        voronoi.style_dot = style_dot_none
        voronoi.play(self, dance.grow, run_time=4, rate_func=slow_into)
        self.wait(2)

        voronoi.style_dot = style_dot_invert
        voronoi.play(self, dance.close, run_time=2, rate_func=there_and_back)
        self.wait(1.5)
        voronoi.play(self, dance.close, run_time=1, rate_func=there_and_back)
        self.wait(.3)
        voronoi.play(self, dance.updown, run_time=3, rate_func=there_and_back)
        self.wait(.8)
        voronoi.play(self, dance.rotate, run_time=3)
