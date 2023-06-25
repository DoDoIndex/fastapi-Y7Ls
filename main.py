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
    from google.oauth2 import service_account
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

    project_id = os.getenv("GOOGLE_CLOUD_STORAGE_PROJECT_ID")
    client_email = os.getenv("GOOGLE_CLOUD_STORAGE_CLIENT_EMAIL")
    private_key = os.getenv("GOOGLE_CLOUD_STORAGE_PRIVATE_KEY")

    credentials_dict = {
        "type": "service_account",
        "project_id": "teak-listener-390900",
        "private_key_id": "55b9090a70101a42ec8298083516ef1e6e3ddb54",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC4P2m5RUR5O+L1\nrG5ukJwx5S7lPpl643/ZgqD0zpRRex16Mago5KtIidrOdWCW8hRpiUF3Qu0eHrOs\n5VNXayuMYg96xEp2y8CQ7eQzkvr+PXKV07impdT8y63sD4sHqKUOvSyB0ar1bHet\nn+S53htxEi3ofVxQaZ/W1DzaKrOzy1io7BYExaE3Cb5Wi1/JIMd9SKjQGF82G2L3\nseNzFE2+89AyqwZxDg1Q06BUexbtEH1UswA7xBsHcsPRYnL47QP/6k92o1VE7SFy\nNluKvECqThHR02BlYOKSunf/8/FPOcltfcqYTQ31PN+on6SMmK00EcW1u4JgyvwX\nzdM5gcxdAgMBAAECggEAAaV/BeremG1Z0zazgbu7Y/6N9Ppiewfmt+4HW+PigB9N\nk+HQniIiMRxN2+iOHXZnCstkdGxt1VLsAzh4aAohe6UFSbEddjxoL+Aqv1ajdUHd\nnbhxSIhbI/HHaXOsTlXD0qLyCR+M+5nFlwP10nH8hLEajAUrKqr+Kx7YUJD8BdHT\npJ4VaOopYnCywjZ5wwmBAopuXAUdeJp7GId9jAz/Vn4jhiphr3YDG02d0e/Jdcxn\nHuzXw3oE7sXfZQS1GCaFEpRIcIRJ8csNBiK2k0ka+1Q0IsmbLL+aZXzvuFRWvSxd\nrAA3MBTdkWpXMj4go3CR2izfL8MOXmghTvEtNbZXIQKBgQDbSiVjudgprq6OhR4e\nXgBYQsW/4XIM+oH+VyKjEbAw1q0mhyizrKOePvrRM9P/ON9i0B9DPt4O4Ymdpd6S\ny/snRg2+M/Eam1fCBrU2HyAqlbIRZcygVxmeC15sDIEOvBdKLKAz82EjB5xKfdA+\nVMAI9w+OhW1IvWanKcCQ5q8oYQKBgQDXF4OFVePUKGTNz4g8q40rbvKugrEfPAkT\n7iH7RoKxy4unrd33IMfRLMNyECX36OGPnENbSGWd/zkidVgSEcsZ8fxLUj7NaXAf\nXaGpx/tZZ22pC5nWCnwu9e/VdPbBp3sJv3Ya3+jbqMFLzcIvQ7Xk2NTyTjU1WUzl\nPFjFWv81fQKBgB8H/QaBs/8iAv2UBNETSEU1HbqrcnI3uNF/Dx24URB4MIR1N+NF\nGNo521BjXyqMp7/Z57KiYNYGQG0Ynch0KRRDq4ow23uCZAbG4DnKacjc6hfgKfa+\nnJdq0G/FzTWClGEgs4Lme+ZzG0DHUQKhB5O9MmxeoTpb4vzgwak/m6XBAoGABNWZ\ndii9CyqxQVL1y+9LJ/vBZpy3YG1YAuOqTdyC2X4qsGUfBQvukcwAxJKKV+0bDMBF\nX0rcRdXTseuTRCy0NOwUcJjzomhJRdsz4/4Drzm85DzHg2EO83tBnbmYRjf+cvSj\nsezwbed4GL0SLT/HWdJpztxlI8LTEJ/vmtf1vn0CgYEAlDqR1xm1Q2kJM7mI7eQ9\nERzLtra2NjRgde6omAPqO4a7zdixIhAU4YRw8MbRv1On9rCFoEmTUrkXonn9OKWg\n3Rub9CqDP8THLcMPrqaiAdYtqx3EcbBCLZuPR0Y/53kH4Jp8Gc0Pz4FJRgd0Iepr\nm/aZLoCHpPrz3guQMOrq6No=\n-----END PRIVATE KEY-----\n",
        "client_email": "stl-uploader-public-3drizz@teak-listener-390900.iam.gserviceaccount.com",
        "client_id": "102978714744283275802",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/stl-uploader-public-3drizz%40teak-listener-390900.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    client = storage.Client(project='teak-listener-390900', credentials=credentials)
    return "SUCCESS 22eeez {} {} {}".format(private_key, client_email, private_key)

    # return storage_credentials['project_id']

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