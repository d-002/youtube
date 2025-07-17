from manim import ManimColor
import numpy as np

BG = ManimColor.from_hex("#161718")
FG = ManimColor.from_hex("#E7E7E1")
GRAY = ManimColor.from_hex("#B6B4B3")

COL1 = ManimColor.from_hex("#E07A5F")
COL2 = ManimColor.from_hex("#81B29A")
COL3 = ManimColor.from_hex("#7A95B8")
COL4 = ManimColor.from_hex("#F2CC8F")
COL5 = ManimColor.from_hex("#9F78B7")

def _make_gradient(col1, col2, n):
    r1, g1, b1 = col1
    r2, g2, b2 = col2
    return [ManimColor.from_rgb(((r1 + t * (r2-r1)) / 255,
                                 (g1 + t * (g2-g1)) / 255,
                                 (b1 + t * (b2-b1)) / 255))
            for t in np.arange(0, 1.000001, 1/n)]

def theme_func_gradient(bounds, cell):
    # gradient from top left to bottom right (careful about y inversion)
    vec = cell.pos - (bounds.tl+bounds.br)*.5
    t = (vec.x/bounds.w - vec.y/bounds.h) + .5
    return t

THEME1 = _make_gradient((0, 224, 138), (153, 51, 255), 10)
THEME2 = _make_gradient((243, 243, 43), (255, 165, 61), 6)
