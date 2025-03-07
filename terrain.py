from py5 import *
import time
import py5, sys
import numpy as np


scale = 1
W, D = None, None
terrain = None
mask = None
terrain_color = None
noise_scale = 0.008 * scale

contour = True

import matplotlib


def settings():
    size(600, 600)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    global W, D, terrain, mask, terrain_color
    W = int(py5.width/scale)
    D = int(py5.height/scale)
    terrain = np.zeros((W, D))
    mask = np.zeros((W, D))

    cur = time.time()

    for y in range(D):
        for x in range(W):
            terrain[x, y] = 2.8*noise(x * noise_scale, y * noise_scale)-1.1

    terrain_color = matplotlib.colormaps['terrain'](terrain) * 255

    for y in range(1, D-1):
        for x in range(1, W-1):
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = x + dx, y + dy
                for i in range(2, 16):
                    alt = i/20.0 * 2.8-1.1
                    if terrain[x, y] < alt < terrain[nx, ny]:
                        mask[x, y] = True
    print('time', time.time() - cur)

def draw():
    no_loop()
    background(255)
    no_stroke()
    for y in range(D):
        for x in range(W):
            if mask[x, y] and contour: fill(0)
            else:
                fill(*terrain_color[x, y])
            rect(x*scale, y*scale, scale, scale)

run_sketch()

