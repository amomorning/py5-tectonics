from py5 import *
import py5
import sys


class SimplePendulum:
    def __init__(self, x, y, r, speed, angle=0):
        self.x = x
        self.y = y
        self.r = r
        self.speed = speed
        self.angle = angle
        self.prev = (x, y, angle)

    def update(self, x=None, y=None):
        self.prev = (self.x, self.y, self.angle)
        if x is not None and y is not None:
            self.x = x
            self.y = y
        self.angle += self.speed
        self.angle %= TWO_PI

    def display(self, c=color(0, 0, 0), sk:py5.Sketch=None):
        sk = sk or py5.get_current_sketch()
        x2 = self.x + self.r * sin(self.angle)
        y2 = self.y + self.r * cos(self.angle)
        sk.stroke(c)
        sk.stroke_weight(6)
        sk.line(self.x, self.y, x2, y2)

        sk.no_stroke()
        sk.fill(c)
        sk.ellipse(x2, y2, 10, 10)
        sk.ellipse(self.x, self.y, 10, 10)


    def display_path(self, c1, c2, sk:py5.Sketch=None):
        x1 = self.prev[0] + self.r * sin(self.prev[2])
        y1 = self.prev[1] + self.r * cos(self.prev[2])
        x2 = self.x + self.r * sin(self.angle)
        y2 = self.y + self.r * cos(self.angle)

        xs = [self.prev[0], self.x, x2, x1]
        ys = [self.prev[1], self.y, y2, y1]
        cs = [c1, c1, c2, c2]

        sk.begin_shape()
        for x, y, c in zip(xs, ys, cs):
            sk.fill(c)
            sk.vertex(x, y)
        sk.end_shape(CLOSE)

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
            pendulum.update(x, y)
            x, y = pendulum.get_end()

    def display(self, c=color(0, 0, 0), sk:py5.Sketch=None):
        for pendulum in self.pendulums:
            pendulum.display(c, sk)

    def display_path(self, c1=color(255, 0, 0), c2=(0, 0, 255), sk:py5.Sketch=None):
        self.pendulums[-1].display_path(c1, c2, sk)

    def get_end(self):
        return self.pendulums[-1].get_end()


def settings():
    size(800, 800, P2D)
    if sys.platform == 'darwin':
        pixel_density(2)


def setup():
    global pg
    background(0)
    pg = create_graphics(800, 800, P2D)


def draw():
    global pendulum, pg, running
    if running:
        pg.begin_draw()
        pg.no_stroke()
        pendulum.display_path(color(43, 66, 146), color(133, 142, 159), pg)
        pg.end_draw()
        background(0)
        image(pg, 0, 0)

        pendulum.update()
        pendulum.display(color(255, 255, 255))


def key_pressed():
    global running
    if py5.key == '1':
        running = not running
    else:
        print_line_profiler_stats()


if __name__ == '__main__':
    running = True
    pendulum = CompoundPendulum(400, 400,
                                [110, 122, 68], # [180, 80, 40]
                                [0.17, -0.07, 0.05], # [-0.06, 0.04, 0.19]
                                [0, 0, 0])
    pg: Py5Graphics = None
    profile_draw()
    run_sketch()