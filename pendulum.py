from py5 import *
from utils import gradient_line
import sys

class SimplePendulum:
    def __init__(self, x, y, r, speed, angle=0):
        self.x = x
        self.y = y
        self.r = r
        self.speed = speed
        self.angle = angle

    def update(self):
        self.angle += self.speed
        self.angle %= TWO_PI

    def display(self):
        x2 = self.x + self.r * sin(self.angle)
        y2 = self.y + self.r * cos(self.angle)
        stroke(0)
        stroke_weight(6)
        line(self.x, self.y, x2, y2)

        no_stroke()
        fill(0)
        ellipse(x2, y2, 10, 10)
        ellipse(self.x, self.y, 10, 10)

    def display_path(self, c1, c2):
        x2 = self.x + self.r * sin(self.angle)
        y2 = self.y + self.r * cos(self.angle)
        gradient_line(self.x, self.y, x2, y2,
                      c1, c2, 30, 3)

    def set_start(self, x, y):
        self.x = x
        self.y = y

    def get_end(self):
        x2 = self.x + self.r * sin(self.angle)
        y2 = self.y + self.r * cos(self.angle)
        return x2, y2


class CompoundPendulum:
    def __init__(self, x, y, rs, speeds, angles):
        self.x, self.y = x, y
        cx, cy = x, y
        self.pendulums = []
        for r, speed, angle in zip(rs, speeds, angles):
            self.pendulums.append(SimplePendulum(cx, cy, r, speed, angle))
            cx = cx + r * sin(angle)
            cy = cy + r * cos(angle)

    def update(self):
        x, y = self.x, self.y
        for pendulum in self.pendulums:
            pendulum.set_start(x, y)
            pendulum.update()
            x, y = pendulum.get_end()

    def display(self):
        for pendulum in self.pendulums:
            pendulum.display()

    def display_path(self, c1=color(255, 0, 0), c2=(0, 0, 255)):
        self.pendulums[-1].display_path(c1, c2)

    def set_start(self, x, y):
        self.x = x
        self.y = y

    def get_end(self):
        return self.pendulums[-1].get_end()




def settings():
    size(800, 800)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    global pendulum
    pendulum = CompoundPendulum(400, 400,
                                [110, 122, 68], # [180, 80, 40]
                                [0.017, -0.007, 0.005], # [-0.006, 0.004, 0.019]
                                [0, 0, 0])
    background(255)


def draw():
    global pendulum
    pendulum.display_path(color(43, 66, 146), color(133, 142, 159))
    pendulum.update()
    # background(255)
    # pendulum.display()


if __name__ == '__main__':
    pendulum:CompoundPendulum = None
    run_sketch()