from py5 import *
import py5, sys
from shapely import Polygon, LineString
import trimesh
import numpy as np
from shapely.ops import unary_union, polygonize, linemerge
from shapely import get_parts


def draw_axis():
    stroke(255, 0, 0)
    line(0, 0, 100, 0)
    stroke(0, 255, 0)
    line(0, 0, 0, 100)
    stroke(0, 0, 255)
    line(0, 0, 0, 0, 0, 100)

def draw_polygon(polygon:Polygon):
    stroke(0)
    no_fill()
    begin_shape()
    for x, y in polygon.exterior.coords:
        vertex(x, y)
    end_shape(CLOSE)

def draw_linestring(polyline: LineString):
    stroke(0)
    begin_shape(LINES)
    for x, y in polyline.coords:
        vertex(x, y)
    end_shape()

def get_random_polygon(n, min_r, max_r):
    angles = np.random.rand(n) * TWO_PI
    angles = sorted(angles)
    print(angles)
    r = np.random.rand(n) * (max_r - min_r) + min_r
    x = np.cos(angles) * r
    y = np.sin(angles) * r
    return Polygon(np.column_stack([x, y]))

def get_random_points(polygon:Polygon, n):
    return trimesh.path.polygons.sample(polygon, n)

def polygon_offset(polygons):
    ret = []
    for ply in polygons:
        ret.append(ply.buffer(-5, join_style=2))
    return ret

def polygon_split(polygon, cutters):
    ls = unary_union(cutters+[polygon.exterior])
    result = polygonize(ls)

    ret = []
    for geom in result:
        print(geom.geom_type)
        if geom.geom_type == 'Polygon':
            ret.append(geom)
    ret = polygon_offset(ret)
    results = []
    for geom in ret:
        if polygon.contains(geom):
            results.append(geom)
    return results


# global camera
rot_x, rot_z = 0, 0

# shape parameter
vs_num, min_r, max_r = 7, 100, 350
site = get_random_polygon(vs_num, min_r, max_r)
cutters = []
results = []


def settings():
    size(800, 800, P3D)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    pass

def draw():
    global site, rot_x, rot_z

    background(255)
    py5.push_matrix()
    py5.translate(py5.width/2, py5.height/2)
    py5.rotate_x(rot_x)
    py5.rotate_z(rot_z)
    draw_polygon(site)
    draw_axis()

    for cutter in cutters:
        draw_linestring(cutter)

    for result in results:
        draw_polygon(result)

    py5.pop_matrix()


def mouse_moved():
    global rot_x, rot_z
    rot_x = remap(py5.mouse_y, 0, py5.width, 0, TWO_PI)
    rot_z = remap(py5.mouse_x, -py5.height, 0, -TWO_PI, 0)

def mouse_released():
    global site, cutters
    if py5.mouse_button == LEFT:
        pts = get_random_points(site, 4)
        angles = np.random.rand(4) * PI
        cutters = []
        for pt, angle in zip(pts, angles):
            d = np.array([cos(angle), sin(angle)]) * py5.width
            cutters.append(LineString([pt - d, pt + d]))

    elif py5.mouse_button == RIGHT:
        site = get_random_polygon(vs_num, min_r, max_r)

def key_pressed():
    global site, cutters, results
    if py5.key == '1':
        results = polygon_split(site, cutters)
        print(len(results))


run_sketch()