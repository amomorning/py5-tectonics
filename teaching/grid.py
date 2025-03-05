from py5 import *
import py5, sys
import numpy as np
from collections import defaultdict, deque
import time

nx, ny = 30, 20
x = np.linspace(0, 800, nx+1)
y = np.linspace(0, 800, ny+1)

X, Y = np.meshgrid(x, y, indexing='ij')
w, d = X[1, 0] - X[0, 0], Y[0, 1] - Y[0, 0]
cx, cy = X + 0.5 * w, Y + 0.5 * d

# global
mask = np.zeros((nx, ny), dtype=bool)
edges = []
dis = []
G = defaultdict(list)

def index(i, j):
    return int(j * nx + i)

def ij(idx):
    return idx % nx, idx // nx

def init():
    global edges, G, mask
    mask = np.zeros((nx, ny), dtype=bool)
    py5.noise_detail(4)
    for i in range(nx):
        for j in range(ny):
            if noise(i, j) < 0.3:
                mask[i, j] = True

    for i in range(nx):
        for j in range(ny):
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ni, nj = i + dx, j + dy
                if 0 <= ni < nx and 0 <= nj < ny and not mask[i, j] and not mask[ni, nj]:
                    u, v = index(i, j), index(ni, nj)
                    edges.append((u, v))
                    G[u].append(v)
                    G[v].append(u)


def bfs(s):
    global dis
    q = deque([s])
    while q:
        u = q.popleft()
        for v in G[u]:
            if dis[v] == float('inf'):
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
        s = int(random(nx * ny))

    dis = [float('inf')] * (nx * ny)
    dis[s] = 0
    cur = time.time()
    bfs(s)
    print('bfs', time.time() - cur)

    dis = [float('inf')] * (nx * ny)
    dis[s] = 0
    cur = time.time()
    dfs(s)
    print('dfs', time.time() - cur)



def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

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

    for u, v in edges:
        stroke(255, 0, 0)
        stroke_weight(2)
        line(cx[ij(u)], cy[ij(u)], cx[ij(v)], cy[ij(v)])

    for i in range(nx):
        for j in range(ny):
            fill(0)
            idx = index(i, j)
            text(dis[idx], cx[i, j], cy[i, j])

def mouse_pressed():
    update(index(py5.mouse_x // w, py5.mouse_y // d))
run_sketch()