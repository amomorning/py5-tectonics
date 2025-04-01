import py5, sys
from py5 import *

from shapely.ops import voronoi_diagram
from shapely import MultiPoint
from utils import *


site = generate_regular_polygon(6, 100, 400, 400, 400)
pts = None
polygons = None
buildings = None
cnt = 5
def llyod(pts, site):
    for i in range(10):
        vor = voronoi_diagram(pts, site)
        pts = []
        for poly in vor.geoms:
            if poly.geom_type == 'Polygon':
                poly = poly.buffer(-5)
                poly = poly.intersection(site)
                if poly.is_empty:
                    continue
                pts.append(poly.centroid)
        pts = MultiPoint(pts)

    plys = []
    for poly in vor.geoms:
        if poly.geom_type == 'Polygon':
            p = poly.buffer(-5)
            ply = p.intersection(site)
            ply = ply.simplify(0.1)
            plys.append(ply)
    return pts, plys


def update():
    global site, pts, polygons, buildings

    pts = MultiPoint(generate_points_in_polygon(site.buffer(-100), cnt))
    pts, polygons = llyod(pts, site)

    buildings = []
    for ply in polygons:
        try:
            buildings.extend(buildings_from_polygon(ply, None, 10, 30))
        except Exception as e:
            buildings.append(ply.buffer(-10))


def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def draw():
    global site, pts, polygons, buildings
    background(140)
    fill(120)
    stroke(0)
    draw_polygon(site)
    # draw_points(pts)
    fill(255)
    for ply in polygons:
        draw_polygon(ply)

    if buildings:
        fill(255, 222, 222)
        stroke(100, 20, 20)
        for b in buildings:
            draw_polygon(b)

def mouse_released(e):
    global site, pts, polygons, cnt
    if py5.mouse_button == LEFT and e.is_shift_down() and cnt > 1:
        cnt -= 1
        update()
    elif py5.mouse_button == LEFT:
        cnt += 1
        update()
    elif py5.mouse_button == RIGHT:
        site = generate_regular_polygon(6, 100, 400, 400, 400)
        update()


update()
run_sketch()

