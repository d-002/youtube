from fast_voronoi import Bounds, Options

def get_bounds(camera):
    cx, cy = camera.frame_center[:2]
    w, h = camera.frame_width, camera.frame_height
    x, y = cx-w/2, cy-h/2
    x, y, w, h = x-20, y-20, w+40, h+40

    return Bounds(x, y, w, h)

options = Options(segments_density=10, divide_lines=True)
