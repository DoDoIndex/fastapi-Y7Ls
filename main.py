from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

import numpy as np
from stl import mesh

def UnitCubeVerts():
    return np.array([
        # bottom square
        [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.0, 0.0],
        # top square
        [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.0, 1.0]])

def RectVerts(length:float, width:float, height:float):
    return UnitCubeVerts()*[length,width,height]

def ContainerVerts(l,w,h,thickness, grow_in = True):
    outerBox = RectVerts(l,w,h)
    if not grow_in:
        thickness *= -1.0
    outerBoxoffset = [thickness,thickness,thickness]
    
    innerBox = RectVerts(l+2*thickness,w+2*thickness,h +thickness)
    outerBox += outerBoxoffset

    return np.concatenate((outerBox, innerBox), axis=0)

# Define the 10 triangles composing the outside of the box
faces = np.array([\

    # outside of the container
    [0,1,3],
    [1,2,3],
    [0,7,4],
    [0,3,7],
    [5,2,1],
    [5,6,2],
    [2,6,3],
    [3,6,7],
    [0,5,1],
    [0,4,5], 

    # inside of the container
    [ 8,11, 9],
    [ 9,11,10],
    [ 8,12,15],
    [ 8,15,11],
    [13, 9,10],
    [13,10,14],
    [10,11,14],
    [11,15,14],
    [ 8, 9,13],
    [ 8,13,12], 

    # lip of the container
    [ 4, 5,12],
    [ 5,13,12],
    [ 5, 6,13],
    [ 6,14,13],
    [ 6, 7,14],
    [ 7,15,14],
    [ 7, 4,15],
    [ 4,12,15],
    ])

def writeContainerStl(l,w,h,t):
    verts = ContainerVerts(l,w,h,t,True)
    # Create the data for the cube
    data = np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype)
    # Create the mesh object
    mesh = mesh.Mesh(data)
    for i, f in enumerate(faces):
        for j in range(3):
            mesh.vectors[i][j] = verts[f[j],:]

    # Save the mesh to an STL file
    return "{}".format(verts)
    #mesh.save('container.stl')

class Msg(BaseModel):
    msg: str


@app.get("/")
async def root():
    return {"message": "Hello World. Welcome to FastAPI!"}


@app.get("/path")
async def demo_get():
    try:
        return {"message": "This is /path endpoint, use a {}".format(writeContainerStl(50,50,50,1))}
    except Exception as e:
        return {"message": "/path made a boom boom! {}".format(str(e))}



@app.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper()}


@app.get("/path/{path_id}")
async def demo_get_path_id(path_id: int):
    return {"message": f"This is /path/{path_id} endpoint, use post request to retrieve result"}