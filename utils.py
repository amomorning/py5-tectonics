import py5

def gradient_line(x1, y1, x2, y2, c1, c2, line_segs=100, line_weight=1):
    py5.stroke_weight(line_weight)

    dx = (x2 - x1) / line_segs
    dy = (y2 - y1) / line_segs

    for i in range(line_segs):
        c = py5.lerp_color(c1, c2, i / line_segs)
        py5.stroke(c)
        py5.line(x1 + i * dx, y1 + i * dy,
             x1 + (i + 1) * dx, y1 + (i + 1) * dy)


def draw_shape(xs, ys, cs, sk:py5.Sketch=None):
    """ draw vertex colored shape

    :param xs: list of x
    :param ys: list of y
    :param cs: list of colors
    :param sk: py5.Sketch or py5.Py5Graphics

    Examples
    --------
    >>> py5.shader(py5.load_shader('shader/vertex_color.glsl'))
    >>> draw_shape([0, 100, 100, 0], [0, 0, 100, 100], [255, 0, 0, py5.color(0, 255, 0)])
    """
    sk = sk or py5.get_current_sketch()
    sk.begin_shape()
    for x, y, c in zip(xs, ys, cs):
        sk.stroke(c)
        sk.fill(c)
        sk.vertex(x, y)
    sk.end_shape(sk.CLOSE)