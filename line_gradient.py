from py5 import *
from random import randint
import sys


def random_color():
    return color(randint(0, 255), randint(0, 255), randint(0, 255))


def settings():
    size(800, 800, P2D) # P2D is needed for gradient
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    background(255)


def draw():
    background(255)
    stroke_weight(4)
    N = 20
    for _ in range(N):
        begin_shape(LINES)
        for i in range(2):
            x, y = randint(0, 800), randint(0, 800)
            stroke(random_color())
            vertex(x, y)
        end_shape()


def key_pressed():
    print_line_profiler_stats()


if __name__ == '__main__':
    profile_draw()
    run_sketch()