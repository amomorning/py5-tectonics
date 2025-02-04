from py5 import *
import py5

def settings():
    size(800, 800)
    pixel_density(2)

def linear_gradient(x1, y1, x2, y2, c1, c2):
    for i in range(800):
        c = lerp_color(c1, c2, i / 800)
        stroke(c)
        line(x1, y1 + i, x2, y2 + i)

def setup():
    background(255)
    linear_gradient(0, 0, 800, 0, color(255, 0, 0), color(0, 0, 255))

run_sketch()