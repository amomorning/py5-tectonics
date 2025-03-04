from py5 import *
import py5, sys
from shapely import Polygon
from utils import *

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
        diffs, ave = evaluate_angles(self.polygon, self.positions, x)
        out["F"] = sum(diffs)


def evaluate_angles(polygon, pos, angles):
    cutters = generate_cutters(pos, angles)
    polygons = polygon_split(polygon, cutters)
    areas = [p.area for p in polygons]

    ave_area = sum(areas) / len(areas)
    return [(a - ave_area) ** 2 for a in areas], ave_area

site = rect_to_polygon(100, 100, 600, 600)
positions = []
evaluated = []



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
    # termination = get_termination("n_eval", 2000)
    print('Start minimizing...')
    res = minimize(problem, algorithm, verbose=True)
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
    diffs, ave = evaluate_angles(site, pts, angles)
    mx = max(diffs)
    for polygon, diff in zip(polygons, diffs):

        p = polygon.buffer(-10)
        fill(255, 255 - diff/mx * 150, 255 - diff/mx * 150 )
        draw_polygon(p)


        centroid = polygon.centroid
        fill(0)
        text(f'{(polygon.area - ave):.2f}', centroid.x, centroid.y)

    fill(0)
    stroke(0)
    text(f'ave area {ave}', 2, 10)


run_sketch()
