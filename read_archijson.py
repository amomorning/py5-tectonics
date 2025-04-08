import archijson.geometry as ag
from shapely import LinearRing, LineString
import json
from py5 import *
import py5



def draw_light():
    lights()
    ambient_light(100, 100, 100)
    point_light(200, 200, 200, 200, 200, 200)


def draw_polygon_volume(polygon:LinearRing, h, z=0):
    stroke(0)

    begin_shape()
    for x, y, _ in polygon.coords:
        vertex(x, y, h+z)
    end_shape(CLOSE)

    for p0, p1 in zip(polygon.coords, polygon.coords[1:]):
        begin_shape()
        vertex(p0[0], p0[1], z)
        vertex(p1[0], p1[1], z)
        vertex(p1[0], p1[1], z + h)
        vertex(p0[0], p0[1], z + h)
        end_shape(CLOSE)

def draw_linestring(polyline: LineString):
    stroke(0)
    begin_shape(LINES)
    for x, y, z in polyline.coords:
        vertex(x, y, z)
    end_shape()

def segments_to_shapely(segments:ag.Segments):
    pts = []
    n = len(segments.coordinates)
    for i in range(n//segments.size):
        pt = segments.coordinates[i*segments.size:(i+1)*segments.size]
        pts.append(pt)
    if segments.closed:
        return LinearRing(pts)
    else:
        return LineString(pts)

def prism_to_extrude_polygon(e):
    seg = ag.call['Segments'](**e['segments'])
    z = e['position']['z']
    h = e['height']
    p = e['properties']
    print(p)
    return segments_to_shapely(seg), h, z, p


rot_x, rot_z = 0, 0
segments = []
volumes = []


def settings():
    size(1000, 1000, P3D)
    pixel_density(2)

def setup():
    global segments, volumes
    data = json.load(open("data/seu.archijson"))

    for e in data['geometryElements']:
        if e['type'] == 'Segments':
            seg = ag.call['Segments'](**e)
            geom = segments_to_shapely(seg)
            segments.append(geom)

        elif e['type'] == 'Prism':
            volumes.append(prism_to_extrude_polygon(e))
        else:
            print(e['type'])
            continue

def draw():
    global rot_x, rot_z
    background(255)
    draw_light()

    py5.push_matrix()
    py5.translate(py5.width/2, py5.height/2)

    py5.rotate_x(rot_x)
    py5.rotate_z(rot_z)

    for seg in segments:
        draw_linestring(seg)

    for v, h, z, p in volumes:
        fill(200)
        if p['type'] == 'block':
            fill(100)
            draw_polygon_volume(v, h, z)
        elif p['color']:
            # p['color'] is 10040098
            # c = int(p['color'], 16)
            c = hex(p['color'])
            r, g, b = int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)
            fill(r, g, b)
            draw_polygon_volume(v, h, z)
        else:
            draw_polygon_volume(v, h, z)

    py5.pop_matrix()

def mouse_moved():
    global rot_x, rot_z
    rot_x = remap(py5.mouse_y, 0, py5.height, 0, PI/2)
    rot_z = remap(py5.mouse_x, 0, py5.width, -PI, PI)
run_sketch()