import trimesh
import colorsys

box = trimesh.creation.box(extents=(1, 1, 1))
cnt = 0

scene = trimesh.Scene()
dirs = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]

colors = [
    (255, 0, 0, 255),
    (255, 255, 0, 255),
    (0, 255, 0, 255),
    (0, 255, 255, 255),
    (0, 0, 255, 255),
    (255, 0, 255, 255),
]

cnt = 0
for dx, dy, dz in dirs:
    x, y, z = 3 + dx, 3 + dy, 3 + dz
    box = trimesh.creation.box(extents=(1, 1, 1))
    box.apply_translation((x, y, z))
    c = colorsys.hsv_to_rgb(cnt / 6, 1, 1)
    color = (c[0]*255, c[1]*255, c[2]*255, 255)
    print(f'({dx}, {dy}, {dz}):{color}')
    for i in range(len(box.faces)):
        box.visual.face_colors[i] = color
    cnt += 1
    scene.add_geometry(box)


scene.show(smooth=False)