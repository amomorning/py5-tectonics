import py5, sys
from py5 import *

from shapely.ops import voronoi_diagram
from utils import *

site = None
pts = None
polygons = None
cnt = 5
def llyod(pts, site):
    for i in range(10):
        vor = voronoi_diagram(pts, site)
        pts = []
        for poly in vor.geoms:
            if poly.geom_type == 'Polygon':
                poly = poly.buffer(-5)
                poly = poly.intersection(site)
                pts.append(poly.centroid)
        pts = MultiPoint(pts)

    plys = []
    for poly in vor.geoms:
        if poly.geom_type == 'Polygon':
            p = poly.buffer(-5)
            plys.append(p.intersection(site))
    return pts, plys


def update():
    global site, pts, polygons
    site = rect_to_polygon(100, 100, 600, 600)
    pts = MultiPoint(generate_points_in_polygon(site.buffer(-100), cnt))
    pts, polygons = llyod(pts, site)



def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def draw():
    global site, pts, polygons
    background(140)
    fill(255)
    draw_polygon(site)
    draw_points(pts)
    no_fill()
    for ply in polygons:
        draw_polygon(ply)

def mouse_released():
    global site, pts, polygons, cnt
    if py5.mouse_button == LEFT:
        cnt += 1
        update()
    if py5.mouse_button == RIGHT:
        cnt -= 1
        update()

update()
run_sketch()

