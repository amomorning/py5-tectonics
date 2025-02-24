from random import randint
import sys
from py5 import *
from collections import deque
import numpy as np
import py5


agents = deque([])
color_mode = False


class Agent:
    def __init__(self, loc, speed, r):
        self.loc = loc
        self.speed = speed
        self.prev = loc
        self.radius = r

    @property
    def m(self):
        return self.radius * self.radius

    def bumping(self, other):
        d = np.linalg.norm(self.loc - other.loc)
        if d < self.radius + other.radius:

            n = self.loc - other.loc
            n /= np.linalg.norm(n)

            v1 = self.speed
            v2 = other.speed

            v1n = np.dot(v1, n)
            v2n = np.dot(v2, n)

            v1_prime = v1 + (2 * other.m / (self.m + other.m)) * (v2n - v1n) * n
            v2_prime = v2 + (2 * self.m / (self.m + other.m)) * (v1n - v2n) * n


            self.speed = v1_prime
            other.speed = v2_prime
            return True
        return False

    def bounce(self):
        if self.loc[0] > py5.width - self.radius or self.loc[0] < self.radius:
            self.speed[0] *= -1
        if self.loc[1] > py5.height - self.radius or self.loc[1] < self.radius:
            self.speed[1] *= -1

    def update(self):
        self.bounce()
        self.prev = self.loc
        self.loc += self.speed

    def display(self, sk:py5.Sketch=None):
        sk = sk or py5.get_current_sketch()
        sk.stroke(0)
        sk.stroke_weight(4)
        sk.circle(self.loc[0], self.loc[1], self.radius * 2)






def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)

def setup():
    background(240)
    py5.color_mode(py5.HSB, 360, 100, 100)
    fill(0, 0, 100)


def draw():
    background(240)

    if color_mode:
        fill(py5.frame_count % 360, 100, 100)
    else:
        fill(0, 0, 100)

    begin_shape()
    for i in range(len(agents)):
        vertex(agents[i].loc[0], agents[i].loc[1])
    end_shape(CLOSE)

    fill(0, 0, 100)
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            agents[i].bumping(agents[j])
        agents[i].update()
        agents[i].display()


def mouse_pressed():
    global color_mode, agents
    if py5.mouse_button == LEFT:
        v = np.array([randint(-5, 5), randint(-5, 5)], dtype=float)
        r = 500/v.dot(v)
        agents.append(Agent(np.array([py5.mouse_x, py5.mouse_y], dtype=float), v, r))
    elif py5.mouse_button == RIGHT:
        agents.popleft()
    else:
        color_mode = not color_mode


run_sketch()