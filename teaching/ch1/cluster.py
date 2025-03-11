from py5 import *
import py5

pts = []
edges = []
eps = 80


parent = []
result_edges = []


def find(u):
    global parent
    if parent[u] == u:
        return u
    parent[u] = find(parent[u])
    return parent[u]

def union(u, v):
    global parent
    pu = find(u)
    pv = find(v)
    if pu == pv:
        return False
    parent[pu] = pv
    return True


def generate_points(n, x, y, r):
    ps = []
    for i in range(n):
        theta = random(TWO_PI)
        d = random(r)
        ps.append((x + d * cos(theta), y + d * sin(theta)))
    return ps

def generate_edges(ps, d):
    n = len(ps)
    es = []
    for i in range(n):
        for j in range(i+1, n):
            if dist(ps[i][0], ps[i][1], ps[j][0], ps[j][1]) < d:
                es.append((i, j))
    return es


def settings():
    size(600, 600)
    pixel_density(2)


def setup():
    color_mode(HSB, 100)


def draw():
    global eps, parent
    background(100, 0, 100)

    for u, v in edges:
        stroke(0)
        line(pts[u][0], pts[u][1], pts[v][0], pts[v][1])

    push_style()
    for u, v in result_edges:
        stroke(0, 100, 100)
        stroke_weight(2)
        line(pts[u][0], pts[u][1], pts[v][0], pts[v][1])
    pop_style()

    for i, (x, y) in enumerate(pts):
        fill(100 * find(i) / len(pts), 100, 100)
        circle(x, y, 10)
        fill(0, 100, 100)
        text_size(16)
        text(f"{i}({find(i)})", x, y)

    fill(0)
    text_size(10)
    text(f"Current EPS: {eps}", 5, 10)
    text(f"Left Click to generate points", 5, 20)
    text(f"Right Click to generate edges", 5, 30)
    text(f"Press '=' to increase eps, '-' to decrease eps", 5, 40)
    text(f"Press '1' to run union-find", 5, 50)
    text(f"Press '[' to run union-find step by step, ']' to reset", 5, 60)


def mouse_released():
    global pts, edges, eps, parent, result_edges
    if py5.mouse_button == LEFT:
        pts = []
        pos = generate_points(5, py5.width//2, py5.height//2, py5.width//2-50)

        for x, y in pos:
            pts.extend(generate_points(5, x, y, 50))

        parent = [i for i in range(len(pts))]
        edges = []
        result_edges = []


    if py5.mouse_button == RIGHT:
        edges = generate_edges(pts, eps)

cnt = 0
def key_released():
    global pts, edges, eps, cnt, result_edges, parent
    if py5.key == '=':
        eps += 10
        edges = generate_edges(pts, eps)
    if py5.key == '-':
        eps -= 10
        edges = generate_edges(pts, eps)

    if py5.key == '1':
        result_edges = []
        for u, v in edges:
            if union(u, v):
                result_edges.append((u, v))

    if py5.key == ']':
        if cnt == 0:
            parent = [i for i in range(len(pts))]
            result_edges = []
        if cnt < len(edges):
            u, v = edges[cnt]
            if union(u, v):
                result_edges.append((u, v))
            cnt += 1

    if py5.key == '[':
        cnt = 0
        result_edges = []
        parent = [i for i in range(len(pts))]


run_sketch()