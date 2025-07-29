from copy import deepcopy

from manim import *

from theme import *
from utils import *

from fast_voronoi import *
from fast_voronoi.utils import get_circle, circle_inter
from fast_voronoi.polygons import Cache, build_pairs, make_polygons

import numpy as np

def get_edges(options, bounds, cells, m):
    cache = Cache(options, bounds, cells)
    pairs = build_pairs(bounds, cache, m, list(cache.cells_inter[m]))

    edges = [[np.array([u.x, u.y, 0])
              for u in cache.get_polygon_edge(i0, i1, m, n)]
             for (n, (i0, i1)) in pairs]

    # sort edges
    indices_left = list(range(len(pairs)))
    indices = []
    indices_i1 = []
    poly_index = -1
    while indices_left:
        change = False
        if poly_index >= 0:
            for i in indices_left:
                _, (i0, i1) = pairs[i]
                if i0 in indices_i1[poly_index]:
                    indices[poly_index].append(i)
                    indices_i1[poly_index].append(i1)
                    indices_left.remove(i)
                    change = True
                    break

        if not change:
            i = indices_left.pop(0)
            indices.append([i])
            indices_i1.append([pairs[i][1][1]])
            poly_index += 1

    edges = [[edges[index] for index in indices_] for indices_ in indices]

    # complete edges
    for edges_ in edges:
        for i, edge in enumerate(edges_):
            edge.append(edges_[(i+1) % len(edges_)][0].copy())

    return sum(edges, start=[])

class Main(Scene):
    def construct(self):
        Text.set_default(color=FG, stroke_color=FG)
        self.camera.background_color = BG

        self.first_scene()
        self.clear()
        self.second_scene()
        self.clear()
        self.third_scene()
        self.clear()
        self.fourth_scene()

    def first_scene(self):
        np.random.seed(100)
        bounds = get_bounds(self.camera, 1)
        cells = [Cell(v2(np.random.uniform(bounds.left+1, bounds.right-1),
                         np.random.uniform(bounds.top+1, bounds.bottom-1)), 1)
                 for _ in range(15)]
        # force cut polygon for later
        cells.append(Cell(v2(-4, 0)))

        polygons = make_polygons(Options(complete_polygons=True), bounds, cells)
        polygons_mo = VGroup(Polygon(*[(u.x, u.y, 0) for u in polygon],
                                     fill_opacity=0, stroke_color=FG)
                             for _, polygon in polygons)

        self.play(FadeIn(polygons_mo))
        self.wait()

        index = 1
        edges1 = get_edges(options, bounds, cells, index)
        polygon = VGroup(VMobject(color=FG).set_points_as_corners(edge)
                         for edge in edges1)

        center = polygons_mo[index].get_center()
        edges2 = deepcopy(edges1)
        for edge, line in zip(edges2, polygon):
            move = line.get_center()-center
            move *= 1/np.linalg.norm(move)

            for i in range(len(edge)):
                edge[i] += move

        self.add(polygon)
        self.play(FadeOut(polygons_mo))

        # shift edges to follow polygon movement
        edges1 = [[pos-center for pos in edge] for edge in edges1]
        edges2 = [[pos-center for pos in edge] for edge in edges2]
        self.play(polygon.animate.move_to(ORIGIN))
        self.wait()

        self.play(AnimationGroup((edge.animate.set_points_as_corners(p)
                                  for edge, p in zip(polygon, edges2)),
                                 lag_ratio=.2), run_time=2)
        self.wait()
        self.play(AnimationGroup((edge.animate.set_points_as_corners(p)
                                  for edge, p in zip(polygon, edges1))))
        self.wait()

        for i in range(len(edges1)):
            edge = polygon[i]
            circle = Circle(radius=.05).set_stroke(COL1).move_to(edge.get_start())
            self.play(circle.animate.set_opacity(0).scale(10),
                      edge.animate.set_stroke(COL1),
                      run_time=.4)
            self.play(edge.animate.set_stroke(FG), run_time=.3)
        self.wait()

        vertex = Dot(color=COL1, radius=.12).move_to(polygon[0].get_end()).set_z_index(1)
        self.play(Create(vertex))
        self.play(polygon[:2].animate.set_stroke(COL1), rate_func=there_and_back)
        self.play(Uncreate(vertex))
        self.wait()

        self.play(polygon.animate.arrange(RIGHT, buff=1).to_edge(UP))
        self.wait()

        self.play(AnimationGroup((edge.animate.set_points_as_corners(p)
                                  for edge, p in zip(polygon, edges1)),
                                 lag_ratio=1), run_time=.7*len(polygon))
        self.wait()

        # add dummy polygon to compensate for a polygon being broken in half
        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        for _ in range(4):
            polygons_mo += Polygon(*dummy, fill_opacity=0, stroke_color=FG)

        weights = np.random.rand(len(cells))*3 + 2
        weights[-1] = 3.1
        def polygons_updater(_):
            # update cells
            t_ = t.get_value()
            for cell, weight in zip(cells, weights):
                cell.weight = 1 + (weight-1)*t_

            index = 0
            for i, points_raw in make_polygons(options, bounds, cells):
                points = [(u.x, u.y, 0) for u in points_raw]

                polygon = polygons_mo[index]
                polygon.set_points_as_corners(points)

                index += 1

            # hide the unused polygons
            for i, polygon in enumerate(polygons_mo):
                polygon.set_stroke(opacity=i < index)

        self.play(polygon.animate.shift(center))

        t = ValueTracker(0)
        polygons_updater(None)
        self.play(FadeIn(polygons_mo))
        self.remove(polygon)

        polygons_mo.add_updater(polygons_updater)
        self.play(t.animate.set_value(1), run_time=2)
        polygons_updater(None)
        polygons_mo.clear_updaters()
        self.wait()

        edges = get_edges(options, bounds, cells, 4)
        rand_indices = list(np.random.permutation(len(edges)))
        polygon = VGroup(VMobject(color=FG).set_points_as_corners(edges[i])
                           for i in rand_indices)

        self.add(polygon)
        self.play(FadeOut(polygons_mo))
        center = polygon.get_center()
        self.play(polygon.animate.shift(-center))
        self.wait()

        self.play(polygon.animate.scale(.5).arrange(RIGHT).to_edge(UP))
        self.wait()

        edges = [[pos-center for pos in edge] for edge in edges]
        self.play(AnimationGroup((polygon[rand_indices.index(i)]
                                  .animate.set_points_as_corners(edge)
                                  for i, edge in enumerate(edges)),
                                 lag_ratio=1), run_time=.7*len(polygon))
        self.wait()

        self.play(polygon.animate.shift(center))
        self.play(FadeIn(polygons_mo))
        self.remove(polygon)
        self.wait()

        self.play(FadeOut(polygons_mo))

    def second_scene(self):
        cells = [Cell(v2(-3, 0), 1.5), Cell(v2(2, 0), 3), Cell(v2(7, 0), 1)]

        bounds = get_bounds(self.camera, 1)
        polygons = make_polygons(options, bounds, cells)
        polygons.sort(key=lambda pair: pair[0])
        polygons = VGroup(Polygon(*[(u.x, u.y, 0) for u in polygon],
                                     fill_opacity=0, stroke_color=FG)
                             for _, polygon in polygons)
        dots = VGroup(Dot((cell.pos.x, cell.pos.y, 0)) for cell in cells)

        cab = get_circle(cells[0], cells[1])
        cac = get_circle(cells[0], cells[2])
        i0, i1 = circle_inter(cab, cac)

        center = (cab.c.x, cab.c.y, 0)
        i0, i1 = (i0.x, i0.y, 0), (i1.x, i1.y, 0)

        circle = Circle(radius=np.sqrt(cab.r2), color=FG).move_to(center)
        A = Dot(radius=.15, color=COL1).move_to(i0).set_z_index(1)
        B = Dot(radius=.15, color=COL1).move_to(i1).set_z_index(1)
        self.play(Write(circle), Write(A), Write(B))
        self.wait()

        diff0, diff1 = np.array(i0)-center, np.array(i1)-center
        angle = abs(np.atan2(diff0[1], diff0[0]) - np.atan2(diff1[1], diff1[0]))
        if angle > np.pi:
            angle -= np.pi
        arc0 = ArcBetweenPoints(diff1, diff0, angle=np.pi-angle, color=COL1, stroke_width=10).shift(center)
        arc1 = ArcBetweenPoints(diff0, diff1, angle=np.pi+angle, color=COL1, stroke_width=10).shift(center)
        self.play(circle.animate.set_stroke(opacity=.2))
        self.play(Write(arc0))
        self.wait()
        self.play(AnimationGroup(FadeOut(arc0), Write(arc1), lag_ratio=.5),
                  run_time=1.5)
        self.wait()
        self.play(FadeOut(arc1))
        self.wait()

        colors = [COL1, COL2, TRANSPARENT]
        for color, polygon in zip(colors, polygons):
            polygon.set_fill(color=color, opacity=.5)

        self.play(Write(dots[:2]),
                  FadeIn(polygons),
                  A.animate.set_color(FG),
                  B.animate.set_color(FG))
        self.wait()

        self.play(polygons.animate.set_stroke(opacity=.2))
        arc0.set_color(FG).set_z_index(1)
        arc1.set_color(FG).set_z_index(1)
        self.play(Write(arc0))
        self.wait()
        self.play(AnimationGroup(FadeOut(arc0), Write(arc1), lag_ratio=.5),
                  run_time=1.5)
        self.wait()
        self.play(FadeOut(arc1),
                  polygons.animate.set_stroke(opacity=0),
                  FadeOut(circle))
        self.wait()

        arc0.set_stroke(width=4)
        segment = Line(dots[0], dots[1], color=FG)
        self.play(Write(segment))
        self.wait()
        self.play(Write(arc0))
        self.wait()

        self.play(FadeOut(polygons, segment, arc0, dots))
        self.wait()

    def third_scene(self):
        bounds = get_bounds(self.camera, 1)
        left, top, w, h = bounds.left, bounds.top, bounds.w, bounds.h

        options = Options(segments_density=10, divide_lines=False)
        bounds = Bounds(left*3, top*3, w*3, h*3)
        np.random.seed(0)
        cells = [Cell(v2(0, 0), 1) for _ in range(30)]

        mkpos = lambda: [v2(np.random.random()*w+left, np.random.random()*h+top)
                         for _ in range(len(cells))]
        mkw = lambda: np.random.random(len(cells))*3+2
        start_pos, end_pos = mkpos(), mkpos()
        weights1, weights2 = mkw(), mkw()

        dummy = [(-1, 0, 0), (1, 0, 0), (0, 1.41, 0)]
        polygons_mo = VGroup(Polygon(*dummy, fill_opacity=1, stroke_color=FG)
                             for _ in range(len(cells)+10))

        def polygons_updater(_):
            # update cells
            t_ = t.get_value()
            for cell, start, end, w1, w2 in zip(cells, start_pos, end_pos, weights1, weights2):
                cell.pos = start + (end-start)*t_
                cell.weight = w1 + (w2-w1)*t_

            index = 0
            for i, points_raw in make_polygons(options, bounds, cells):
                points = [(u.x, u.y, 0) for u in points_raw]

                polygon = polygons_mo[index]
                polygon.set_points_as_corners(points)
                color = get_color_from_t(THEME1, theme_func_gradient(bounds, cells[i]))
                polygon.set_fill(color)

                index += 1

            # hide the unused polygons
            for i, polygon in enumerate(polygons_mo):
                polygons_mo[i].set_opacity(i < index)

        self.add(polygons_mo)

        t = ValueTracker(0)
        polygons_mo.add_updater(polygons_updater)
        self.play(t.animate.set_value(1), rate_func=linear, run_time=30)
        polygons_mo.clear_updaters()

    def fourth_scene(self):
        A = Dot(color=COL1).shift(2*LEFT).set_z_index(1)
        B = Dot(color=COL1).shift(2*RIGHT).set_z_index(1)

        def make_arc(n):
            points = []
            for i in range(0, n+1):
                angle = np.pi - np.pi*i/n
                points.append((np.cos(angle)*2, np.sin(angle)*2, 0))

            arc.set_points_as_corners(points)

        def updater(_):
            make_arc(round(t.get_value()))

        line = Line(A, B)
        arc = VMobject(color=FG)
        make_arc(50)

        self.wait()
        self.play(Write(A), Write(B))
        self.play(Write(line))
        self.wait()
        self.play(ReplacementTransform(line, arc))
        self.wait()

        self.play(FadeOut(arc))
        t = ValueTracker(1)
        make_arc(1)
        self.play(FadeIn(arc))
        self.wait()

        arc.add_updater(updater)
        self.play(t.animate.set_value(50), rate_func=rush_into, run_time=3)
        arc.clear_updaters()
        self.wait()

        self.play(FadeOut(A, B, arc))
