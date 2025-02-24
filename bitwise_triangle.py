import py5, sys
from py5 import *

def settings():
    size(512, 512)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    no_stroke()
    for i in range(py5.width):
        for j in range(py5.height):
            if i & j:
                fill(0)
            else:
                fill(255)
            rect(i, j, 1, 1)


run_sketch()