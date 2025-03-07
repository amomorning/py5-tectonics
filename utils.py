import py5
import numpy as np
import shapely
import math, random
from shapely.ops import polygonize, unary_union

# list of pure function

def get_rectangle_centroid(x, y, w, h, theta):
    w, h = w/2, h/2
    cs = np.cos(theta)
    sn = np.sin(theta)
    pts = [
        [x - w * cs - h * sn, y - w * sn + h * cs],
        [x + w * cs - h * sn, y + w * sn + h * cs],
        [x + w * cs + h * sn, y + w * sn - h * cs],
        [x - w * cs + h * sn, y - w * sn - h * cs]
    ]
    return shapely.Polygon(pts)

def get_rectangle_bottom_left(x, y, w, h, theta):
    cs = np.cos(theta)
    sn = np.sin(theta)
    pts = [[x, y], [x + w * cs, y + w * sn],
           [x + w * cs - h * sn, y + w * sn + h * cs], [x - h * sn, y + h * cs]]
    return shapely.Polygon(pts)

def rect_to_polygon(x, y, w, h):
    return shapely.Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)])


def transform_polygon(polygon:shapely.Polygon, s):
    bb = polygon.bounds
    sx, sy = bb[2]-bb[0], bb[3]-bb[1]
    return shapely.affinity.translate(shapely.affinity.scale(polygon, s/sx, s/sy), s, s)

def draw_points(pts):
    if isinstance(pts, shapely.MultiPoint):
        pts = [(p.x, p.y) for p in pts.geoms]
    for x, y in pts:
        py5.circle(x, y, 10)

def draw_polygon(polygon:shapely.Polygon):
    py5.begin_shape()
    for x, y in polygon.exterior.coords:
        py5.vertex(x, y)

    for hole in polygon.interiors:
        py5.begin_contour()
        for x, y in hole.coords:
            py5.vertex(x, y)
        py5.end_contour()
    py5.end_shape(py5.CLOSE)

def draw_linestring(polyline: shapely.LineString):
    py5.begin_shape(py5.LINES)
    for x, y in polyline.coords:
        py5.vertex(x, y)
    py5.end_shape()

def polygon_split(polygon, cutters):
    ls = unary_union(cutters+[polygon.exterior])
    result = polygonize(ls)
    return [r for r in result if r.is_valid and r.area > 100 and polygon.contains(r)]


def generate_points_in_polygon(polygon:shapely.Polygon, n):
    pts = []
    while len(pts) < n:
        x = py5.random(polygon.bounds[0], polygon.bounds[2])
        y = py5.random(polygon.bounds[1], polygon.bounds[3])
        if polygon.contains(shapely.Point(x, y)):
            pts.append((x, y))
    return pts

def generate_cutters(pts, angles):
    cutters = []
    d = 800
    for (x, y), angle in zip(pts, angles):
        cutters.append(shapely.LineString([(x - math.cos(angle) * d, y - math.sin(angle) * d),
                                   (x + math.cos(angle) * d, y + math.sin(angle) * d)]))
    return cutters

