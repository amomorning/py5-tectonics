from py5 import *
import time
import py5, sys
import numpy as np


scale = 1
W, D = None, None
terrain = None
mask = None
noise_scale = 0.008 * scale

contour = True

def color_map(v):
    if v < 0:
        return color(remap(v, 0, -0.5, 60, 10),
                     remap(v, 0, -0.5, 160, 10),
                     remap(v, 0, -0.5, 240, 80))
    if 0 < v < 0.3:
        return color( remap(v, 0, 0.3, 120, 150),
                      remap(v, 0, 0.3, 180, 255), 120)
    return color(remap(v, 0.3, 0.9, 150, 255),
                 remap(v, 0.3, 0.9, 120, 255),
                 remap(v, 0.3, 0.9, 100, 255))

def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    global W, D, terrain, mask
    W = int(py5.width/scale)
    D = int(py5.height/scale)
    terrain = np.zeros((W, D))
    mask = np.zeros((W, D))

    cur = time.time()

    for y in range(D):
        for x in range(W):
            terrain[x, y] = 2*noise(x * noise_scale, y * noise_scale)-1

    for y in range(1, D-1):
        for x in range(1, W-1):
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = x + dx, y + dy
                for alt in [-0.4, 0, 0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]:
                    if terrain[x, y] < alt < terrain[nx, ny]:
                        mask[x, y] = True

def draw():
    no_loop()
    background(255)
    no_stroke()
    for y in range(D):
        for x in range(W):
            if mask[x, y] and contour: fill(0)
            else:
                fill(color_map(terrain[x, y]))
            rect(x*scale, y*scale, scale, scale)

run_sketch()

