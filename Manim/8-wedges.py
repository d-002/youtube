from copy import deepcopy

from manim import *

from theme import *
from utils import *

from fast_voronoi import *
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
            for i in range(index, len(polygons_mo)):
                polygons_mo[i].set_opacity(0)

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
        pass
