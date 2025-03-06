from py5 import *
import py5, sys
import numpy as np
from collections import deque, defaultdict
import time

nx, ny = 30, 30
x = np.linspace(0, 800, nx+1)
y = np.linspace(0, 800, ny+1)

X, Y = np.meshgrid(x, y, indexing='ij') # cell top-left corner
w, d = X[1, 0] - X[0, 0], Y[0, 1] - Y[0, 0]

cx, cy = X + 0.5 * w, Y + 0.5 * d # center of the cell

# global
mask = np.zeros((nx, ny), dtype=bool)
edges = []
G = defaultdict(list)
dis = [float('inf') for _ in range(nx * ny)]


def index(i, j):
    return int(j * nx + i)

def ij(idx):
    return idx % nx, idx // nx

def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def init():
    global mask, edges, G
    edges = []
    G = defaultdict(list)
    mask = np.zeros((nx, ny), dtype=bool)
    noise_seed(random_int(1000))

    for i in range(nx):
        for j in range(ny):
            if noise(i, j) < 0.3:
                mask[i, j] = True

    for i in range(nx):
        for j in range(ny):
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                ux, uy = i + dx, j + dy
                if 0 <= ux < nx and 0 <= uy < ny:
                    if not mask[i, j] and not mask[ux, uy]:
                        u, v = index(i, j), index(ux, uy)
                        edges.append((u, v))
                        G[u].append(v)
                        G[v].append(u)

def bfs(s):
    global dis
    dis = [float('inf') for _ in range(nx * ny)]
    q = deque([s])
    dis[s] = 0

    while q:
        u = q.popleft()
        for v in G[u]:
            if dis[v] > dis[u] + 1:
                dis[v] = dis[u] + 1
                q.append(v)

def dfs(u):
    global dis
    for v in G[u]:
        if dis[v] > dis[u] + 1:
            dis[v] = dis[u] + 1
            dfs(v)


def update(s=None):
    global dis
    if s is None:
        s = random_int(nx * ny)

    cur = time.time()
    bfs(s)
    print('bfs', time.time() - cur)

    cur = time.time()
    dis = [float('inf') for _ in range(nx * ny)]
    dis[s] = 0
    dfs(s)
    print('dfs', time.time() - cur)


def setup():
    init()
    update()


def draw():
    background(255)
    no_stroke()

    for i in range(nx):
        for j in range(ny):
            if mask[i, j]:
                fill(0)
            else:
                fill(255)
            rect(X[i, j], Y[i, j], w, d)
            fill(0)
            text(f"{dis[index(i, j)]}", cx[i, j], cy[i, j])

    stroke(255, 0, 0)
    for u, v in edges:
        line(cx[ij(u)], cy[ij(u)], cx[ij(v)], cy[ij(v)])


def key_released():
    if py5.key == '1':
        init()
        update()

def mouse_released():
    idx = index(py5.mouse_x // w, py5.mouse_y // d)
    update(idx)

run_sketch()