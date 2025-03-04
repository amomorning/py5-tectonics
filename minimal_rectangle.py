import trimesh
from py5 import *
from shapely import Polygon
from utils import *

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.termination.ftol import MultiObjectiveSpaceTermination
from pymoo.termination.robust import RobustTermination


class MaxRectangleProblem(ElementwiseProblem):
    def __init__(self, polygon:Polygon):
        bb = polygon.bounds

        super().__init__(n_var=5, n_obj=1, n_ieq_constr=1,
                         xl=np.array([bb[0], bb[1], 0, 0, -np.pi]),
                         xu=np.array([bb[2], bb[3], bb[2]-bb[0], bb[3]-bb[1], np.pi]))
        self.polygon = polygon

    def _evaluate(self, x, out, *args, **kwargs):
        rect = get_rectangle_centroid(*x)
        out["F"] = -x[2] * x[3]
        out["G"] = -1.0 if self.polygon.contains(rect) else 1.0


def settings():
    size(800, 800, P2D)
    if sys.platform == 'darwin':
        pixel_density(2)


ply, rect = None, None
def update_ply():
    global ply
    ply = trimesh.path.polygons.random_polygon(5)
    ply = transform_polygon(ply, 400)


def update_rect():
    global ply, rect

    problem = MaxRectangleProblem(ply)
    algorithm = NSGA2(
        pop_size=100,
        n_offsprings=100,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )
    # termination = RobustTermination(
        # MultiObjectiveSpaceTermination(tol=0.00005, n_skip=5), period=20)
    res = minimize(problem,
                   algorithm,
                   verbose=True)

    if res.opt is not None:
        rect = get_rectangle_centroid(*res.opt.get("X")[0])


def setup():
    background(240)
    global ply, rect

    update_ply()
    update_rect()


def draw():
    background(240)
    global ply, rect
    if ply is not None:
        stroke_weight(2)
        stroke(0)
        draw_polygon(ply)


    if rect is not None:
        stroke(255, 0, 0)
        draw_polygon(rect)

        fill(0)
        stroke(0)
        text(f'rect area {rect.area}', 2, 10)
        fill(255)

def mouse_pressed():
    global ply, rect
    if py5.mouse_button == LEFT:
        update_ply()
        rect = None
    if py5.mouse_button == RIGHT:
        update_rect()

def key_pressed():
    global ply, rect
    if py5.key == '1':
        pts = [
            (3, 2), (4.5, 2), (2, 4.5), (2, 3),
            (-2, 3), (-2, 4.5), (-4.5, 2), (-3, 2),
            (-3, -2), (-4.5, -2), (-2, -4.5), (-2, -3),
            (2, -3), (2, -4.5), (4.5, -2), (3, -2)
        ] # Ho'olheyak Polygon
        ply = Polygon(pts)
        ply = transform_polygon(ply, 400)
        rect = None

run_sketch()
