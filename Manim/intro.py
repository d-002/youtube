from random import seed, random
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
        x, y, w, h = x-10, y-10, w+20, h+20

        self.bounds = Bounds(x, y, w, h)

    def init1(self, voronoi):
        black, white = voronoi.cells[:2]
        black.pos = v2(self.bounds.right/2, 0)
        white.pos = v2(self.bounds.left, 0)
        black.weight = 1
        white.weight = 1

        for i in range(2, len(voronoi.cells)):
            cell = voronoi.cells[i]
            cell.weight = 100
            cell.pos = v2(self.bounds.left, i)

        voronoi.update()

    def arrive1(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = (1-t) * self.bounds.right
        white.weight = 5 - 4*t

    def arrive2(self, voronoi, t):
        black, white = voronoi.cells[:2]
        black.pos.x = t * (.2*self.bounds.right)
        white.pos.x = (1-t*.8) * self.bounds.left

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

    def init3(self, voronoi):
        black, white, green = voronoi.cells[:3]

        black.pos = v2(.2*self.bounds.left, 0)
        white.pos = v2(.2*self.bounds.right, 0)

        green.weight = 1
        green.pos = v2(0, self.bounds.bottom)
        voronoi.update()

    def arrive3(self, voronoi, t):
        black, white, green = voronoi.cells[:3]

        y = t * .15*self.bounds.bottom
        black.pos.y = y
        white.pos.y = y

        green.pos.y = (1 - t*.9) * self.bounds.top

    def cut(self, voronoi, t):
        black, white, green = voronoi.cells[:3]

        y = (1 - 2*t) * .15*self.bounds.bottom
        black.pos.y = y
        white.pos.y = y

        green.pos.y = (1 - 2*t) * .1*self.bounds.top

    def init_all(self, voronoi):
        seed(0)

        for i in range(3, len(voronoi.cells)):
            cell = voronoi.cells[i]
            cell.weight = 1

            x, y = random()-.5, random()-.5
            x += -.3 if x < 0 else .3
            y += -.3 if y < 0 else .3
            cell.pos = v2(x*self.bounds.right, y*self.bounds.bottom)

        voronoi.update()


class Intro(Scene):
    def construct(self):
        def style_poly_transparent(polygon: Polygon, color: tuple):
            polygon.set_stroke(color)
            polygon.set_fill(color, opacity=.5)

        def style_poly_fill(polygon: Polygon, color: tuple):
            polygon.set_stroke(width=0)
            polygon.set_fill(color, opacity=1)

        def style_dot_invert(dot: Dot, color: ManimColor):
            r, g, b = color.to_rgb()
            r, g, b = int(r*255), int(g*255), int(b*255)

            if r == g == b:
                r, g, b = 255-r, 255-g, 255-b
            else:
                if r+g+b < 384:
                    r, g, b = min(r+50, 255), min(g+50, 255), min(b+50, 255)
                else:
                    r, g, b = max(r-50, 0), max(g-50, 0), max(b-50, 0)

            dot.set_color(ManimColor.from_rgb((r, g, b)))

        dance = Dance(self.camera)
        bounds = dance.bounds

        options = Options(segments_density=10, divide_lines=True)
        cells = [Cell(v2(i, 0), 1) for i in range(8)]
        colors = [BLACK, WHITE, GREEN, YELLOW, BLUE, RED, PURPLE, ORANGE]

        funcs = style_poly_fill, style_dot_invert
        voronoi = VoronoiAnim(options, bounds, cells, colors, funcs, True)

        """
        text = Text('Headphones recommended',
                    font_size=20)
        self.play(Write(text, run_time=2))
        self.wait(1)
        self.play(FadeOut(text, run_time=5))
        """

        self.add(voronoi.polygons)
        self.add(voronoi.dots)
        dance.init1(voronoi)

        """
        voronoi.play(self, dance.arrive1, run_time=2, rate_func=rush_from)
        self.wait(1.5)
        voronoi.play(self, dance.arrive2, run_time=4, rate_func=double_smooth)
        self.wait(2.5)
        voronoi.play(self, dance.close, run_time=2, rate_func=there_and_back)
        self.wait(1.5)
        voronoi.play(self, dance.close, run_time=1, rate_func=there_and_back)
        self.wait(.5)
        voronoi.play(self, dance.updown, run_time=4, rate_func=there_and_back)
        self.wait(1.5)
        voronoi.play(self, dance.rotate, run_time=5)
        self.wait(1.5)
        """

        dance.init3(voronoi)

        voronoi.play(self, dance.arrive3, run_time=5, rate_func=double_smooth)
        voronoi.play(self, dance.cut, run_time=5, rate_func=there_and_back)
        self.wait(.5)

        everything = VGroup(voronoi.polygons, voronoi.dots)
        # ok I give up for this animation
        self.play(FadeOut(everything), run_time=1)
        dance.init_all(voronoi)
        self.play(FadeIn(everything), run_time=1)
        self.wait(1)
        self.play(FadeOut(everything), run_time=1)
        everything.scale(.45)
        self.play(FadeIn(everything), run_time=1)
        self.wait(2)
