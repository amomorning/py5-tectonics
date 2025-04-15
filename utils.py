import py5
import math, random
import numpy as np
import shapely
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

def generate_regular_polygon(n, minR, maxR, x=0, y=0):
    pts = []
    for i in range(n):
        r = random.uniform(minR, maxR)
        theta = i*2*math.pi/n
        pts.append((r*math.cos(theta) + x, r*math.sin(theta) + y))

    return shapely.Polygon(pts)

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


def extend_segment(p1, p2, d=0.01):
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    return (x1 - d * dx, y1 - d * dy), (x2 + d * dx, y2 + d * dy)


def points_on_linearring(linearring, n):
    pts = []
    delta = 1-(n-1)/n
    rnd = random.random() * delta
    for i in range(n):
        x, y = linearring.interpolate(i/n + rnd, normalized=True).xy
        pts.append((x[0], y[0]))
    return pts


def buildings_from_polygon(polygon, n=None, d=5, depth=18):
    inner = polygon.buffer(-d-depth)
    outer = polygon.buffer(-d/2)

    if n is None:
        n = len(outer.exterior.coords)
    points = points_on_linearring(inner.exterior, n)

    ls = []
    for p in points:
        perp_point = shapely.ops.nearest_points(outer.exterior, shapely.Point(p))[0]
        perp_point = (perp_point.x, perp_point.y)
        p1, p2 = extend_segment(p, perp_point)
        ls.append(shapely.LineString([p1, p2]))
    ls = unary_union(ls + [outer.exterior, inner.exterior])

    results = polygonize(ls)
    buildings = []
    for b in results:
        if type(b) is shapely.Polygon:
            b = b.buffer(-d/2, join_style=2)
            if inner.contains(b):
                continue
            buildings.append(b)
    return buildings


