import numpy as np
from py5 import *
import py5, sys

nx, ny = 9, 12
x = np.linspace(0, 800, nx)
y = np.linspace(0, 800, ny)

def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    for i in range(nx-1):
        for j in range(ny-1):
            w = x[i+1] - x[i]
            h = y[j+1] - y[j]
            if (i+j) % 2 == 0:
                fill(255)
            else:
                fill(120)
            rect(x[i], y[j], w, h)


run_sketch()