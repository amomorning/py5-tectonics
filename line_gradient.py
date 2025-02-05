from py5 import *
from utils import gradient_line
from random import randint

def settings():
    size(800, 800)
    pixel_density(2) # This is for retina displays in Macs


def setup():
    background(255)
    for i in range(200):
        x1, y1 = randint(0, 800), randint(0, 800)
        x2, y2 = randint(0, 800), randint(0, 800)
        gradient_line(x1, y1, x2, y2, color(255, 0, 0), color(0, 0, 255), 20, 8)


if __name__ == '__main__':
    run_sketch()