import uuid

import tempfile
import numpy as np
from stl import mesh
from stl import Mode

from ..service import upload_google_cloud_storage


# Define the 10 triangles composing the outside of the box
faces = np.array(
    [  # outside of the container
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
        # inside of the container
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
        # lip of the container
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


def container_verts(
    length: float, width: float, height: float, thickness: float, grow_in=True
):
    outerBox = rect_verts(length, width, height)
    if not grow_in:
        thickness *= -1.0
    outerBoxoffset = [thickness, thickness, thickness]

    innerBox = rect_verts(
        length + 2 * thickness, width + 2 * thickness, height + thickness
    )
    outerBox += outerBoxoffset

    if not grow_in:
        return  np.concatenate((outerBox, innerBox), axis=0)
    else:
        return  np.concatenate((innerBox, outerBox), axis=0)


def create_shape(length, width, height, thickness):
    verts = container_verts(length, width, height, thickness, True)
    # Create the data for the cube
    data = np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype)
    # Create the mesh object
    cMesh = mesh.Mesh(data)
    for i, f in enumerate(faces):
        for j in range(3):
            cMesh.vectors[i][j] = verts[f[j], :]

    filename = "{}_{}x{}x{}x{}.stl".format(
        uuid.uuid4(), length, width, height, thickness
    )

    # Save the mesh to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=True) as temp_file:
        cMesh.save(temp_file.name, mode=Mode.ASCII)
        # Upload to Google Cloud Storage
        simple_box = {
            "label": "Simple Box",
            "url": upload_google_cloud_storage(
                filename, temp_file.name, "stl-bucket-public-v1-3drizz"
            ),
        }
        return [simple_box]
