from collections import defaultdict
import numpy as np
from py5 import *
import py5, sys
import heapq

nx, ny = 20, 20
x = np.linspace(0, 800, nx+1)
y = np.linspace(0, 800, ny+1)

X, Y = np.meshgrid(x, y, indexing='ij')
w, d = X[1, 0] - X[0, 0], Y[0, 1] - Y[0, 0]
cx, cy = X + 0.5 * w, Y + 0.5 * d

dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
mask = np.zeros((nx, ny), dtype=bool)

edges = []
G = defaultdict(list)
dis = []


def index(i, j):
    return int(j * nx + i)

def ij(idx):
    return idx % nx, idx // nx

def dijkstra(s):
    global dis
    q = [(0, s)]
    dis = [float('inf')] * (nx * ny)
    dis[s] = 0
    vis = [False] * (nx * ny)
    prev = [-1] * (nx * ny)

    while q:
        d, u = heapq.heappop(q)
        if vis[u]:
            continue
        vis[u] = True
        for v in G[u]:
            if not vis[v] and dis[v] > dis[u] + 1:
                dis[v] = dis[u] + 1
                heapq.heappush(q, (dis[v], v))
                prev[v] = u
    return prev

def init():
    global edges, G, mask
    edges = []
    G = defaultdict(list)

    noise_seed(random_int(1000))
    mask = np.zeros((nx, ny), dtype=bool)

    py5.noise_detail(2)
    for i in range(nx):
        for j in range(ny):
            if noise(i, j) < 0.3:
                mask[i, j] = True

    for i in range(nx):
        for j in range(ny):
            for dx, dy in dirs:
                if 0 <= i + dx < nx and 0 <= j + dy < ny:
                    if mask[i, j] or mask[i + dx, j + dy]:
                        continue
                    edges.append((index(i, j), index(i + dx, j + dy)))


    for u, v in edges:
        G[u].append(v)
        G[v].append(u)


def update(s=None):
    if s is None:
        s = random_int(nx * ny)
    dijkstra(s)



def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    init()
    update()

def draw():
    for i in range(nx):
        for j in range(ny):
            fill(255)
            no_stroke()
            if mask[i, j]:
                fill(0)

            rect(X[i, j], Y[i, j], w, d)
            # circle(cx[i, j], cy[i, j], 10)


    stroke(255, 0, 0)
    for u, v in edges:
        line(cx[ij(u)], cy[ij(u)], cx[ij(v)], cy[ij(v)])

    for i in range(nx):
        for j in range(ny):
            fill(0)
            idx = index(i, j)
            text(f'{dis[idx]}', cx[i, j], cy[i, j])


def mouse_released():
    update(index(py5.mouse_x // w, py5.mouse_y // d))

def key_pressed():
    if py5.key == '1':
        init()
        update()

run_sketch()