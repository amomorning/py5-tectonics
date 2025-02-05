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