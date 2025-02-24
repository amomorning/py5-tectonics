from py5 import *
import py5, sys


def settings():
    size(600, 600)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    for i in range(py5.width):
        line(i, 0, i, (py5.width - i) ^ i)


run_sketch()