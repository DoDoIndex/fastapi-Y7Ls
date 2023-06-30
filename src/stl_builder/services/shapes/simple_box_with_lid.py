import uuid

import tempfile
import numpy as np
from stl import mesh
from stl import Mode

from ..service import upload_google_cloud_storage


# Define the triangles composing the box
box_faces = np.array(
    [  # outside of the box
        [0, 1, 3],
        [1, 2, 3],
        [0, 7, 4],
        [0, 3, 7],
        [5, 2, 1],
        [5, 6, 2],
        [2, 6, 3],
        [3, 6, 7],
        [0, 5, 1],
        [0, 4, 5],
        # inside of the box
        [8, 11, 9],
        [9, 11, 10],
        [8, 12, 15],
        [8, 15, 11],
        [13, 9, 10],
        [13, 10, 14],
        [10, 11, 14],
        [11, 15, 14],
        [8, 9, 13],
        [8, 13, 12],
        # lip of the box
        [4, 5, 12],
        [5, 13, 12],
        [5, 6, 13],
        [6, 14, 13],
        [6, 7, 14],
        [7, 15, 14],
        [7, 4, 15],
        [4, 12, 15],
    ]
)
# Define the triangles composing the lid
lid_faces = np.array([
    # top of the lid
    # bottom
    #[0,1,3],
    #[1,2,3],

    # top
    [4,7,5],
    [5,7,6],

    # front
    [0,7,4],
    [0,3,7],

    # back
    [5,2,1],
    [5,6,2],

    # right
    [2,6,3],
    [3,6,7],

    # left
    [0,5,1],
    [0,4,5], 

   ## bottom of the lid
    # bottom
    [8,9,11],
    [9,10,11],

    ## top
    #[12,15,13],
    #[13,15,14],

    # front
    [8,15,12],
    [8,11,15],

    # back
    [13,10,9],
    [13,14,10],

    # right
    [10,14,11],
    [11,14,15],

    # left
    [8,13,9],
    [8,12,13], 

    # combination of the two pieces
    #front joining
    [ 3,0, 15],
    [ 0,12,15],
    #back joining
    [ 1,2, 13],
    [ 2,14,13],
    #right joining
    [ 2,3,14],
    [ 3,15,14],
    #left joining
    [ 0,1, 12],
    [ 1,13,12],
    ])

def unit_cube_verts():
    return np.array(
        [
            # bottom square
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            # top square
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
        ]
    )


def rect_verts(length: float, width: float, height: float):
    return unit_cube_verts() * [length, width, height]


def box_verts(
    length: float, width: float, height: float, thickness, grow_in=True
):
    outerBox = rect_verts(length, width, height)
    if not grow_in:
        thickness *= -1.0
    outerBoxoffset = [thickness, thickness, thickness]

    innerBox = rect_verts(
        length + 2 * thickness, width + 2 * thickness, height + thickness
    )
    outerBox += outerBoxoffset

    return np.concatenate((outerBox, innerBox), axis=0)

def lid_verts(
    length: float,width: float,height: float,thickness: float
):
    lidtop = rect_verts(length, width, height)
    bottomoffset = [thickness,thickness,-thickness]

    lidbottom = rect_verts(length-2*thickness,width-2*thickness,thickness)
    lidbottom += bottomoffset
    return  np.concatenate((lidtop, lidbottom), axis=0)


def generate_stl(verts: np.array, faces:np.array):
    data = np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype)
    mesh_object = mesh.Mesh(data)
    for i, f in enumerate(faces):
        for j in range(3):
            mesh_object.vectors[i][j] = verts[f[j], :]
    return mesh_object

def create_shape(length, width, height, thickness):
    # BOX
    box_mesh = generate_stl(box_verts(length, width, height, thickness, True),box_faces)

    box_filename = "{}_{}x{}x{}x{}.stl".format(
        uuid.uuid4(), length, width, height, thickness
    )

    # Save the mesh to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=True) as temp_file:
        box_mesh.save(temp_file.name, mode=Mode.ASCII)
        # Upload to Google Cloud Storage
        box = {
            "label": "Box",
            "url": upload_google_cloud_storage(
                box_filename, temp_file.name, "stl-bucket-public-v1-3drizz"
            ),
        }

    # LID
    lid_mesh = generate_stl(lid_verts(length, width, height, thickness),lid_faces)
    lid_filename = "{}_{}x{}x{}x{}.stl".format(
        uuid.uuid4(), length, width, height, thickness
    )

    # Save the mesh to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=True) as temp_file:
        lid_mesh.save(temp_file.name, mode=Mode.ASCII)
        # Upload to Google Cloud Storage
        lid = {
            "label": "Lid",
            "url": upload_google_cloud_storage(
                lid_filename, temp_file.name, "stl-bucket-public-v1-3drizz"
            ),
        }
    return [box, lid]
