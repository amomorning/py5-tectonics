from py5 import *
from shapely import Polygon
import trimesh, shapely
import sys, math
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.crossover import Crossover
from pymoo.core.mutation import Mutation
from pymoo.optimize import minimize
from pymoo.operators.sampling.lhs import LHS
import numpy as np
from utils import *
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.pso import PSO

class GroupedSBX(SBX):

    def __init__(self, group_size=5, prob=0.9, eta=15):
        super().__init__(prob, eta)
        self.group_size = group_size
        self.eta_c = eta
        self.prob = prob


    def _do(self, problem, X, **kwargs):
        n_parents, n_matings, n_var = X.shape
        assert n_var % self.group_size == 0, "n_var必须能被group_size整除"
        n_groups = n_var // self.group_size

        # 初始化子代数组
        off = np.empty_like(X)

        # 确定需要交叉的交配
        cross = np.random.random(n_matings) < self.prob
        cross_idx = np.where(cross)[0]
        no_cross_idx = np.where(~cross)[0]

        # 处理不交叉的情况
        off[:, no_cross_idx, :] = X[:, no_cross_idx, :]

        if len(cross_idx) == 0:
            return off

        # 提取需要交叉的父代
        a, b = X[:, cross_idx, :]

        # 获取变量边界
        xl = problem.xl if problem.has_bounds() else np.full(n_var, -np.inf)
        xu = problem.xu if problem.has_bounds() else np.full(n_var, np.inf)

        # 计算每组生成一个beta值
        beta = self._get_beta(len(cross_idx), n_groups)
        beta_expanded = np.repeat(beta, self.group_size, axis=1)

        # 生成随机数决定交叉方向
        rand = np.random.random((len(cross_idx), n_var))

        # 计算子代
        c1 = 0.5 * ((1 + beta_expanded) * a + (1 - beta_expanded) * b)
        c2 = 0.5 * ((1 - beta_expanded) * a + (1 + beta_expanded) * b)

        # 选择c1或c2
        mask = rand <= 0.5
        off[0, cross_idx, :] = np.where(mask, c1, c2)
        off[1, cross_idx, :] = np.where(mask, c2, c1)

        # 确保不越界
        np.clip(off[:, cross_idx, :], xl, xu, out=off[:, cross_idx, :])

        return off

    def _get_beta(self, n_matings, n_groups):
        u = np.random.random((n_matings, n_groups))
        beta = np.where(u <= 0.5, 
                        (2 * u) ** (1 / (self.eta_c + 1)), 
                        (2 * (1 - u)) ** (-1 / (self.eta_c + 1)))
        return beta

# 自定义分组交叉算子

class GroupedCrossover(Crossover):
    def __init__(self, prob=0.9):
        # 2 parents → 2 offspring
        super().__init__(2, 2)
        self.prob = prob

    def _do(self, problem, X, **kwargs):
        """
        X.shape = (n_offspring, n_matings, n_var)
        我们先把 n_var 拆成 (n_blocks, 5)
        """
        n_off, n_mat, n_var = X.shape
        assert n_var % 5 == 0, "n_var 必须能被 5 整除"
        n_blocks = n_var // 5

        # 准备输出
        Y = np.full_like(X, np.inf)

        for i in range(n_mat):
            p1 = X[0, i, :].copy()
            p2 = X[1, i, :].copy()
            c1, c2 = p1.copy(), p2.copy()

            # 以 prob 的概率交换每个 block
            if np.random.rand() < self.prob:
                for b in range(n_blocks):
                    start = b * 5
                    end   = start + 5
                    if np.random.rand() < 0.5:
                        # 交换 block
                        c1[start:end], c2[start:end] = p2[start:end], p1[start:end]

            Y[0, i, :] = c1
            Y[1, i, :] = c2

        return Y

class GroupedMutation(Mutation):
    def __init__(self, eta=20, block_prob=0.1):
        """
        eta        — 多项式变异的分布指数
        block_prob — 每个 5 维块触发变异的概率
        """
        super().__init__()
        # 内部使用一个概率恒为 1 的多项式变异算子来对块做“原子”变异
        self._pm = PM(eta=eta, prob=1.0)
        self.block_prob = block_prob

    def _do(self, problem, X, **kwargs):
        """
        X.shape = (n_individuals, n_var)

        我们将 n_var 拆成 n_blocks = n_var // 5 组，每组 5 维
        对于每个个体、每个块，以 block_prob 概率调用多项式变异
        """
        n_ind, n_var = X.shape
        assert n_var % 5 == 0, "n_var 必须能被 5 整除"
        n_blocks = n_var // 5

        # 先复制一份作为输出
        Y = X.copy()

        for i in range(n_ind):
            for b in range(n_blocks):
                start = b * 5
                end   = start + 5
                if np.random.rand() < self.block_prob:
                    # 构造子块 (1, 5)
                    block = Y[i:i+1, start:end]
                    # 调用底层 PolynomialMutation._do
                    mutated = self._pm._do(problem, block)
                    Y[i, start:end] = mutated[0]

        return Y

class RectsInPolygon(ElementwiseProblem):
    def __init__(self, polygon: Polygon, n_rects=2, i_angle=math.pi/10):

        bb = polygon.bounds
        n_vars = n_rects * 5 # (x, y, w, h, angle) - centered rotated rectangle
        xl = np.array([bb[0], bb[1], 0, 0, -np.pi] * n_rects)
        xu = np.array([bb[2], bb[3], bb[2]-bb[0], bb[3]-bb[1], np.pi] * n_rects)

        super().__init__(n_var=n_vars, n_obj=2, n_ieq_constr=2,
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
        out["F"] = [-unions.area, -sum_area]
        # out["F"] = -unions.area
        
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
    coords = [
        (0, 0),     # 左底点
        (2, 4),     # 左上角
        (4, 2),     # 中间最低点
        (6, 4),     # 右上角
        (8, 0),     # 右底点
        (4, -2),     # 中下点
    ]
    ply = Polygon(coords)
    ply = transform_polygon(ply, 400)


def update_rect_greedy(n_rects=2, attempts=20000, i_angle=math.pi/10):
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
    problem = RectsInPolygon(ply, n_rects=2)
    algorithm = NSGA2(
        pop_size=200,
        n_offsprings=100,
        sampling=LHS(),
        # crossover=GroupedSBX(group_size=5, prob=0.9, eta=15),
        crossover=GroupedCrossover(),
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
    update_rect()
    # update_rect_greedy()

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
        update_rect()
        # update_rect_greedy()

run_sketch()

