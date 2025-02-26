from random import shuffle

import py5, sys
from py5 import *

pts = []
edges = []
eps = 20

parent = []
tree_edges = []


def find(u):
    global parent
    if parent[u] == u:
        return u
    pu = find(parent[u])
    parent[u] = pu
    return pu

def union(u, v):
    global parent
    if parent[u] == parent[v]:
        return False
    u = find(u)
    v = find(v)
    parent[v] = u
    return True


def generate_sample_positions(n, x, y, r):
    pos = []
    for i in range(n):
        angle = random() * TWO_PI
        d = random() * r
        pos.append((x + d * cos(angle), y + d * sin(angle)))
    return pos


def generate_edges(pts, d):
    es = []
    for i in range(len(pts)):
        for j in range(i):
            if dist(pts[i][0], pts[i][1], pts[j][0], pts[j][1]) < d:
                es.append((i, j))
    return es




def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    pass

def draw():
    global pts, parent
    background(250)


    for i, p in enumerate(pts):
        fill(150)
        circle(p[0], p[1], 5)
        fill(0)
        text(f'{i}({find(i)})', p[0], p[1])

    py5.push_style()
    for u, v in edges:
        stroke(0)
        line(pts[u][0], pts[u][1], pts[v][0], pts[v][1])
    py5.pop_style()


    py5.push_style()
    for u, v in tree_edges:
        stroke(255, 0, 0)
        stroke_weight(2)
        line(pts[u][0], pts[u][1], pts[v][0], pts[v][1])
    py5.pop_style()


    fill(0)
    text('Press 1 to generate edges', 5, 10)
    text('Press + or - to change eps', 5, 20)
    text(f'Current eps: {eps}', 5, 30)


def mouse_released():
    global pts, edges, eps, tree_edges, parent
    num_pos = random_int(5, 10)
    positions = generate_sample_positions(num_pos, py5.width//2, py5.height//2, py5.width//2-50)
    pts = []
    edges = []
    tree_edges = []

    for pos in positions:
        num_pts = random_int(20, 50)
        r = random_int(20, 50)
        pts.extend(list(generate_sample_positions(num_pts, pos[0], pos[1], r)))

    shuffle(pts)
    parent = list(range(len(pts)))

cnt = 0
def key_released():
    global edges, eps, parent, tree_edges, cnt
    if py5.key == '1':
        edges = generate_edges(pts, eps)

    if py5.key == '2':
        tree_edges = []
        parent = list(range(len(pts)))
        for u, v in edges:
            if union(u, v):
                tree_edges.append((u, v))

    if py5.key == ']':
        if cnt == 0:
            tree_edges = []
            parent = list(range(len(pts)))
        if cnt < len(edges):
            u, v = edges[cnt]
            if union(u, v):
                tree_edges.append((u, v))
            cnt += 1

    if py5.key == '[':
        cnt = 0

    if py5.key == '=':
        eps += 5
        edges = generate_edges(pts, eps)

    if py5.key == '-':
        eps -= 5
        edges = generate_edges(pts, eps)


run_sketch()