from fast_voronoi import Bounds, Options

def get_bounds(camera, margin):
    cx, cy = camera.frame_center[:2]
    w, h = camera.frame_width, camera.frame_height
    x, y = cx-w/2, cy-h/2
    x, y, w, h = x-margin, y-margin, w+2*margin, h+2*margin

    return Bounds(x, y, w, h)

options = Options(segments_density=10, divide_lines=True)
