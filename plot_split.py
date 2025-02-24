from py5 import *
import py5, sys
from shapely import Polygon, LineString
import trimesh
import numpy as np
from shapely.ops import unary_union, polygonize


def draw_light():
    lights()
    ambient_light(100, 100, 100)
    point_light(255, 255, 255, 200, 200, 200)
    directional_light(255, 255, 255, 1, -1, 1)
    spot_light(255, 255, 255, 0, 0, 0, 0, -1, 1, 45, 2)


def draw_axis():
    stroke(255, 0, 0)
    line(0, 0, 800, 0)
    stroke(0, 255, 0)
    line(0, 0, 0, 800)
    stroke(0, 0, 255)
    line(0, 0, 0, 0, 0, 800)


def draw_polygon(polygon:Polygon):
    stroke(0)
    no_fill()
    begin_shape()
    for x, y in polygon.exterior.coords:
        vertex(x, y)
    end_shape(CLOSE)


def draw_polygon_volumn(polygon:Polygon, height):
    stroke(0)
    fill(200)

    begin_shape()
    for x, y in polygon.exterior.coords:
        vertex(x, y, height)
    end_shape(CLOSE)

    for p0, p1 in zip(polygon.exterior.coords, polygon.exterior.coords[1:]):
        begin_shape()
        vertex(p0[0], p0[1], 0)
        vertex(p1[0], p1[1], 0)
        vertex(p1[0], p1[1], height)
        vertex(p0[0], p0[1], height)
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
    r = np.random.rand(n) * (max_r - min_r) + min_r
    x = np.cos(angles) * r
    y = np.sin(angles) * r
    return Polygon(np.column_stack([x, y]))


def get_random_points(polygon:Polygon, n):
    return trimesh.path.polygons.sample(polygon, n)


def polygon_offset(polygons, size):
    polygons = [p.buffer(size, join_style=2) for p in polygons]
    return [p for p in polygons if p.geom_type == 'Polygon' and p.is_valid]


def polygon_split(polygon, cutters):
    ls = unary_union(cutters+[polygon.exterior])
    result = polygonize(ls)

    ret = []
    for geom in result:
        if geom.geom_type == 'Polygon':
            ret.append(geom)
    ret = polygon_offset(ret, -10)
    return [geom for geom in ret if geom.is_valid and polygon.contains(geom) and geom.area > 50]


# global camera
rot_x, rot_z = 0, 0

# shape parameter
vs_num, min_r, max_r = 7, 100, 350
site = get_random_polygon(vs_num, min_r, max_r)
cutters = []
results = []


def settings():
    size(1600, 800, P3D)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    pass


def draw():
    global site, rot_x, rot_z

    background(255)
    draw_light()

    py5.push_matrix()
    py5.translate(py5.width/2, py5.height/2)

    py5.rotate_x(rot_x)
    py5.rotate_z(rot_z)

    draw_axis()
    draw_polygon(site)

    for cutter in cutters:
        draw_linestring(cutter)

    for result in results:
        draw_polygon_volumn(*result)

    py5.pop_matrix()


def mouse_moved():
    global rot_x, rot_z
    rot_x = remap(py5.mouse_y, 0, py5.height, 0, PI/2)
    rot_z = remap(py5.mouse_x, 0, py5.width, -PI, PI)


def mouse_released():
    global site, cutters, results
    if py5.mouse_button == LEFT:
        pts = get_random_points(site, 4)
        angles = np.random.rand(4) * PI
        cutters = []
        for pt, angle in zip(pts, angles):
            d = np.array([cos(angle), sin(angle)]) * py5.width
            cutters.append(LineString([pt - d, pt + d]))

        results = [(p, random_int(30, 60)) for p in polygon_split(site, cutters)]

    elif py5.mouse_button == RIGHT:
        site = get_random_polygon(vs_num, min_r, max_r)
        cutters = []
        results = []


def key_pressed():
    global site, cutters, results
    pass


run_sketch()