from py5 import *
from shapely import Polygon
import trimesh, shapely
import sys, math
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
import numpy as np
from utils import *
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.pso import PSO

class RectsInPolygon(ElementwiseProblem):
    def __init__(self, polygon: Polygon, n_rects=2, i_angle=math.pi/10):

        bb = polygon.bounds
        n_vars = n_rects * 5 # (x, y, w, h, angle) - centered rotated rectangle
        xl = np.array([bb[0], bb[1], 0, 0, -np.pi] * n_rects)
        xu = np.array([bb[2], bb[3], bb[2]-bb[0], bb[3]-bb[1], np.pi] * n_rects)

        super().__init__(n_var=n_vars, n_obj=1, n_ieq_constr=2,
                         xl=xl,
                         xu=xu)
        self.n_rects = n_rects
        self.i_angle = i_angle
        self.polygon = polygon

    def _evaluate(self, x, out, *args, **kwargs):
        rects = []
        for i in range(self.n_rects):
            rect = get_rectangle_centroid(*x[i*5:i*5+5])
            rects.append(rect)
        
        max_angle = -1
        for i in range(self.n_rects):
            for j in range(i):
                if rects[i].intersects(rects[j]):
                    max_angle = max(max_angle, abs(x[i*5+4] - x[j*5+4]))

        unions = rects[0]
        for rect in rects[1:]:
            unions = unions.union(rect)

        sum_area = sum([r.area for r in rects])
        # out["F"] = [-unions.area, -sum_area]
        out["F"] = -unions.area
        
        contains = -1.0 if self.polygon.contains(unions) else 1.0
        fit_angle = 1.0 if max_angle < self.i_angle else -1.0
        out["G"] = [contains, fit_angle]

ply = None
rects = []

def settings():
    size(800, 800, P2D)
    if sys.platform == 'darwin':
        pixel_density(2)

def update_ply():
    global ply
    ply = trimesh.path.polygons.random_polygon(5)
    # coords = [
    #     (0, 0),     # 左底点
    #     (2, 4),     # 左上角
    #     (4, 2),     # 中间最低点
    #     (6, 4),     # 右上角
    #     (8, 0),     # 右底点
    #     (4, -2),     # 中下点
    # ]
    # ply = Polygon(coords)
    ply = transform_polygon(ply, 400)


def update_rect_greedy(n_rects=3, attempts=20000, i_angle=math.pi/10):
    global ply, rects
    if ply is None:
        return

    bb = ply.bounds
    width, height = bb[2]-bb[0], bb[3]-bb[1]

    rects = []
    angles = []

    for k in range(n_rects):
        best_rect = None
        best_area = -1
        for i in range(attempts):
            x = random.uniform(bb[0], bb[2])
            y = random.uniform(bb[1], bb[3])
            w = random.uniform(10, width)
            h = random.uniform(10, height)
            angle = random.uniform(-np.pi, np.pi)
            if any(min(abs(angle - a), 2 * np.pi - abs(angle - a)) < i_angle for a in angles):
                continue
            rect = get_rectangle_centroid(x, y, w, h, angle)
            if not ply.contains(rect):
                continue
            unions = rect
            tot_area = 0
            for r in rects:
                if rect.intersects(r):
                    unions = unions.union(r)
                else:
                    tot_area += r.area
            tot_area += unions.area
            if tot_area > best_area:
                best_area = tot_area
                best_rect = rect
        if best_rect is None: continue
        rects.append(best_rect)


def update_rect():
    global ply, rects
    problem = RectsInPolygon(ply, n_rects=3)
    algorithm = NSGA2(
        pop_size=100,
        n_offsprings=100,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )
    # algorithm = DE(
    #     pop_size=100,
    #     sampling=FloatRandomSampling(),
    #     variant="DE/rand/1/bin",
    #     CR=0.1,
    #     dither="vector",
    #     jitter=True
    # )
    # algorithm = PSO(
    #     # sampling=FloatRandomSampling(),
    #     pop_size=50,
    # )

    res = minimize(problem,
                   algorithm,
                   verbose=True)

    if res.opt is not None:
        rects = [get_rectangle_centroid(*res.opt.get("X")[0][i*5:i*5+5]) for i in range(problem.n_rects)]


def setup():
    background(240)

    update_ply()
    # update_rect()
    update_rect_greedy()

def draw():
    background(240)
    if ply is not None:
        stroke_weight(2)
        stroke(0)
        fill(255)
        draw_polygon(ply)

    if rects:
        stroke(255, 0, 0)
        no_fill()
        for rect in rects:
            draw_polygon(rect)
        
        fill(0)
        stroke(0)
        unions = rects[0]
        for rect in rects[1:]:
            unions = unions.union(rect)
        text(f"Area: {unions.area}", 10, 20)

def mouse_pressed():
    global ply, rects
    if py5.mouse_button == LEFT:
        update_ply()
        rects = []
    if py5.mouse_button == RIGHT:
        # update_rect()
        update_rect_greedy()

run_sketch()

