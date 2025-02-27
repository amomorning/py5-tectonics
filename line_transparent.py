from py5 import *
import py5
from random import randint
import sys


def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    global pg
    background(255)
    stroke_weight(randint(5, 20))
    stroke(randint(0, 255), randint(0, 255), randint(0, 255))
    pg = create_graphics(800, 800)


def draw():
    global x, y, start
    pg.begin_draw()
    pg.background(255, 6)
    if start:
        pg.line(py5.mouse_x, py5.mouse_y, x, y)
        x, y = py5.mouse_x, py5.mouse_y
    pg.end_draw()
    image(pg, 0, 0)


def mouse_pressed():
    global x, y, start
    pg.stroke_weight(randint(5, 20))
    pg.stroke(randint(0, 255), randint(0, 255), randint(0, 255))
    x, y = py5.mouse_x, py5.mouse_y
    start = not start


if __name__ == '__main__':
    pg:Py5Graphics = None
    x, y, start = None, None, None

    run_sketch()
