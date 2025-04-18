import archijson.geometry as ag
import json, py5, trimesh, sys
from shapely import LinearRing, LineString, Polygon


def draw_light():
    py5.lights()
    py5.ambient_light(100, 100, 100)
    py5.point_light(200, 200, 200, 200, 200, 200)


def coords_to_points(coords, size):
    pts = []
    n = len(coords)
    for i in range(n//size):
        pt = coords[i*size:(i+1)*size]
        pts.append(pt)
    return pts


def segments_to_shapely(seg:ag.Segments, polygon=False):
    pts = coords_to_points(seg.coordinates, seg.size)

    if polygon:
        return Polygon(pts)
    if seg.closed:
        return LinearRing(pts)
    else:
        return LineString(pts)


def segments_to_trimesh(e):
    seg = ag.call['Segments'](**e)
    pts = coords_to_points(seg.coordinates, seg.size)
    if seg.size == 3:
        pts = [(x, y) for x, y, z in pts]
    return trimesh.creation.extrude_polygon(Polygon(pts), height=0.1)


def prism_to_trimesh(e):
    seg = ag.call['Segments'](**e['segments'])
    pts = coords_to_points(seg.coordinates, seg.size)
    if seg.size == 3:
        pts = [(x, y) for x, y, z in pts]
    h = e['height']
    mesh = trimesh.creation.extrude_polygon(Polygon(pts), height=h)
    if e['position']['z']:
        mesh.apply_translation((0, 0, e['position']['z']))
    return mesh


def mesh_to_trimesh(e):
    vs = ag.Vertices(**e['vertices'])
    fs = ag.Faces(**e['faces'])

    pts = coords_to_points(vs.coordinates, vs.size)

    faces = []
    cur = 0
    for cnt, sz in zip(fs.count, fs.size):
        for i in range(cnt):
            if sz == 3:
                faces.append(fs.index[cur:cur+sz])
                cur += sz
            else:
                print('mesh not triangulate yet, skipping')
    return trimesh.Trimesh(pts, faces)



rot_x, rot_z = 0, 0
segments = []
meshes = []
shapes = []

def settings():
    py5.size(1000, 1000, py5.P3D)
    if sys.platform == 'darwin':
        py5.pixel_density(2)


def setup():
    global segments, shapes, meshes
    data = json.load(open("data/flexurban_export.archijson", 'r', encoding='utf-8'))

    for e in data['geometryElements']:
        if e['type'] == 'Segments':
            seg = ag.call['Segments'](**e)
            # if seg.filled:
            #     meshes.append(segments_to_trimesh(e)) # need for export in flexurban
            segments.append(segments_to_shapely(seg))
        elif e['type'] == 'Prism':
            meshes.append(prism_to_trimesh(e))
        elif e['type'] == 'Mesh':
            meshes.append(mesh_to_trimesh(e))
        else:
            print(e['type'])
            continue

    for mesh in meshes:
        shapes.append(py5.convert_shape(mesh))

    for seg in segments:
        shapes.append(py5.convert_shape(seg))


def draw():
    global rot_x, rot_z
    py5.background(255)
    draw_light()

    py5.push_matrix()
    py5.translate(py5.width/2, py5.height/2)

    py5.rotate_x(rot_x)
    py5.rotate_z(rot_z)

    for shp in shapes:
        py5.shape(shp)

    py5.pop_matrix()


def mouse_moved():
    global rot_x, rot_z
    rot_x = py5.remap(py5.mouse_y, 0, py5.height, 0, py5.PI/2)
    rot_z = py5.remap(py5.mouse_x, 0, py5.width, -py5.PI, py5.PI)


def key_pressed():
    if py5.key == 's': # save
        scene = trimesh.Scene(meshes)
        scene.export('data/output.obj')
        print('Scene saved!')


py5.run_sketch()