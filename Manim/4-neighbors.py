from manim import *

from theme import *
from utils import *

from fast_voronoi import *
from fast_voronoi.utils import perp_bisector
from fast_voronoi.neighbors import is_neighbor
from fast_voronoi.intersections import all_intersections

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        bounds = get_bounds(self.camera, 0)
        left, top, w, h = bounds.left, bounds.top, bounds.w, bounds.h
        bounds = Bounds(left*3, top*3, w*3, h*3)

        cells = [Cell(v2(x, y), 1) for x, y in [(-4, 0), (4, 0), (0, h*1.5), (0, -h*1.5), (-w*1.5, 10)]]
        A, B, C = cells[:3]
        dots = VGroup(Dot(radius=.15, color=FG).move_to((cell.pos.x, cell.pos.y, 0))
                      for cell in cells)

        self.play(Write(dots))
        self.wait()

        segment = Line((0, 2, 0), (0, -2, 0), color=FG)
        self.play(Write(segment))
        self.wait()

        ends = get_ends_from_bisector(bounds, perp_bisector(A.pos, B.pos))
        line = Line(*ends, color=FG)
        self.play(ReplacementTransform(segment, line))

        length = len(cells)
        t = ValueTracker(0)

        def dots_updater(t):
            for cell, dot in zip(cells, dots):
                u = cell.pos
                dot.move_to((u.x, u.y, 0))

        def first_cells_updater(t):
            clamp = lambda t: 0 if t < 0 else 1 if t > 1 else t
            t2 = clamp(t*3)
            t3 = clamp(t*3-1)
            t4 = clamp(t*3-2)

            cells[2].pos.y = h*1.5 - t2*h*.8
            cells[3].pos.y = -h*1.5 + t3*h*.8
            cells[4].pos = v2(-w*1.5 * (1-t4), 10 * (1-t4))

        def second_cells_updater(t):
            cells[0].pos = v2(-4 + t, -2*t)
            cells[2].pos = v2(-2*t, h*.7 - t*h*.3)
            cells[3].pos.y = -h*.7 - t*h*.8
            cells[4].pos = v2(-w*1.5 * t, 10*t)

        def lines_updater(_):
            # move cells and dots
            cells_updater(t.get_value())

            # update dots

            # compute and update lines
            neighbors = [[] for _ in range(length)]
            for i in range(length):
                for j in range(i+1, length):
                    if i == j:
                        continue
                    if is_neighbor(bounds, cells, i, j):
                        neighbors[i].append(j)

            intersections, _ = all_intersections(bounds, cells, neighbors)

            index = 0
            for i, cell_a in enumerate(cells):
                for j in neighbors[i]:
                    cell_b = cells[j]

                    points = []
                    for inter in intersections:
                        if cell_a in inter.cells and cell_b in inter.cells:
                            u = inter.pos
                            points.append((u.x, u.y, 0))

                    if len(points) != 2:
                        continue

                    line = lines[index]
                    line.put_start_and_end_on(*points)
                    line.set_opacity(1)
                    index += 1

            for i in range(index, len(lines)):
                lines[i].set_opacity(0)

        self.remove(line)

        lines = VGroup(Line((-1, 0, 0), (1, 0, 0), color=FG) for _ in range(length*(length-1)//2))
        cells_updater = first_cells_updater
        dots.add_updater(dots_updater)
        lines.add_updater(lines_updater)
        lines_updater(None)

        self.add(lines)
        self.wait()

        self.play(t.animate.set_value(1), rate_func=smoothstep, run_time=3)
        cells_updater(1)
        self.wait()

        cells_updater = second_cells_updater
        t.set_value(0)
        self.play(t.animate.set_value(1), run_time=2)

        dots.clear_updaters()
        lines.clear_updaters()
        self.wait()
