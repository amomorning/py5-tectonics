from py5 import *


def gradient_line(x1, y1, x2, y2, c1, c2, line_segs=100, line_weight=1):
    stroke_weight(line_weight)

    dx = (x2 - x1) / line_segs
    dy = (y2 - y1) / line_segs

    for i in range(line_segs):
        c = lerp_color(c1, c2, i / line_segs)
        stroke(c)
        line(x1 + i * dx, y1 + i * dy,
             x1 + (i + 1) * dx, y1 + (i + 1) * dy)


def settings():
    size(800, 800)
    pixel_density(2) # This is for retina displays in Macs


def setup():
    background(255)
    gradient_line(100, 100, 700, 700, color(255, 0, 0), color(0, 0, 255), 20, 8)


run_sketch()