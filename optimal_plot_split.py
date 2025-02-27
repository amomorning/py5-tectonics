from py5 import *
import py5, sys
from shapely.ops import polygonize, unary_union
from shapely import Polygon, LineString, Point

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.termination import get_termination

class AngleCut(ElementwiseProblem):
    def __init__(self, polygon:Polygon, positions):
        super().__init__(n_var=len(positions), n_obj=1, n_constr=0, xl=0, xu=PI)
        self.polygon = polygon
        self.positions = positions

    def _evaluate(self, x, out, *args, **kwargs):
        diffs = evaluate_angles(self.polygon, self.positions, x)
        out["F"] = sum(diffs)


def evaluate_angles(polygon, positions, angles):
    cutters = generate_cutters(positions, angles)
    polygons = polygon_split(polygon, cutters)
    areas = [p.area for p in polygons]

    ave_area = sum(areas) / len(areas)
    return [(a - ave_area) ** 2 for a in areas]



def rect_to_polygon(x, y, w, h):
    return Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)])

site = rect_to_polygon(100, 100, 600, 600)
positions = []
evaluated = []

def draw_polygon(polygon:Polygon):
    begin_shape()
    for x, y in polygon.exterior.coords:
        vertex(x, y)

    for hole in polygon.interiors:
        begin_contour()
        for x, y in hole.coords:
            vertex(x, y)
        end_contour()
    end_shape(CLOSE)

def draw_linestring(polyline: LineString):
    begin_shape(LINES)
    for x, y in polyline.coords:
        vertex(x, y)
    end_shape()

def polygon_split(polygon, cutters):
    ls = unary_union(cutters+[polygon.exterior])
    result = polygonize(ls)
    return [r for r in result if r.is_valid and r.area > 100 and polygon.contains(r)]


def generate_points_in_polygon(polygon:Polygon, n):
    pts = []
    while len(pts) < n:
        x = random(polygon.bounds[0], polygon.bounds[2])
        y = random(polygon.bounds[1], polygon.bounds[3])
        if polygon.contains(Point(x, y)):
            pts.append((x, y))
    return pts

def generate_cutters(pts, angles):

    cutters = []
    d = 800
    for (x, y), angle in zip(pts, angles):
        cutters.append(LineString([(x - cos(angle) * d, y - sin(angle) * d),
                                   (x + cos(angle) * d, y + sin(angle) * d)]))
    return cutters



def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    draw_polygon(site)
    N = 10
    pts=  generate_points_in_polygon(site, N)


    problem = AngleCut(site, pts)
    algorithm = NSGA2(
        pop_size=100,
        n_offsprings=100,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )
    termination = get_termination("n_eval", 1000)
    print('Start minimizing...')
    res = minimize(problem, algorithm, termination, verbose=False)
    print(f'Done {res.opt.get("X")}')

    if res.opt is not None:
        angles = res.opt.get("X")[0]
    else:
        angles = [random(TWO_PI) for _ in range(N)]

    cutters = generate_cutters(pts, angles)
    for x, y in pts:
        circle(x, y, 10)

    for cutter in cutters:
        draw_linestring(cutter)

    polygons = polygon_split(site, cutters)
    diffs = evaluate_angles(site, pts, angles)
    mx = max(diffs)
    for polygon, diff in zip(polygons, diffs):
        p = polygon.buffer(-10)
        stroke(0, 0, 255)
        fill(255, diff/mx * 150 + 100, diff/mx * 150 + 100)
        draw_polygon(p)
    stroke(0)



run_sketch()
