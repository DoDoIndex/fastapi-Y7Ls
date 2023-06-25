import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
    from stl import mesh 
    from stl import Mode
    from sshfs import SSHFileSystem
    from google.cloud import storage
    import uuid
    import time
    import os
    import json
    
    start = time.time()
    verts = ContainerVerts(l,w,h,t,True)
    time1 = time.time()
    # Create the data for the cube
    data = np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype)
    # Create the mesh object
    cMesh = mesh.Mesh(data)
    for i, f in enumerate(faces):
        for j in range(3):
            cMesh.vectors[i][j] = verts[f[j],:]
    
    stl_filename = "{}_{}x{}x{}x{}.stl".format(uuid.uuid4(), l, w, h, t)

    storage_credentials_string = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    storage_credentials = json.loads(storage_credentials_string)
    storage_client = storage.Client.from_service_account_json(storage_credentials)
    return "SUCCESS"

    # Save the mesh to a temporary file
    with NamedTemporaryFile(suffix='.stl', delete=True) as temp_file:
        cMesh.save(temp_file.name, mode=Mode.ASCII)

        # Upload the file to Google Cloud Storage

        storage_client = storage.Client.from_service_account_json(storage_credentials)
        bucket_name = "stl-bucket-public-v1-3drizz "
        destination_blob_name = stl_filename
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file.name)

    url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    return url

    # time2 = time.time()
    # fs = SSHFileSystem( "217.23.4.125", username="admin_rizztest", password="cT7Q2LTfvG")
    # time3 = time.time()
    # filename = "{}_{}x{}x{}x{}.stl".format(uuid.uuid4(), l, w, h, t)
    # with fs.open(filename, 'wb') as fh:
    #     cMesh.save(filename, fh, mode=Mode.BINARY)
    # time4 = time.time()
    # # Save the mesh to an STL file
    # return "https://static-test.3drizz.com/{}, time1 {}, time2 {}, time3 {}, time4 {}".format(filename, time1-start, time2-time1, time3-time2, time4-time3)

class Msg(BaseModel):
    msg: str


@app.get("/")
async def root():
    return {"message": "Hello World. Welcome to FastAPI!"}


@app.get("/path")
async def demo_get():
    return {"url": "{}".format(writeContainerStl(50,50,50,1))}
    # try:
    #     return {"url": "{}".format(writeContainerStl(50,50,50,1))}
    # except Exception as e:
    #     return {"message": "/path made a boom boom! {}".format(str(e))}



@app.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper()}


@app.get("/path/{path_id}")
async def demo_get_path_id(path_id: int):
    return {"message": f"This is /path/{path_id} endpoint, use post request to retrieve result"}