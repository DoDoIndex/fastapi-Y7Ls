from fastapi import APIRouter

from .service import write_container_stl


router = APIRouter(prefix='/v1')


@router.get("/")
async def homepage() -> str:
    return "hello world"


@router.get("/3d-box")
async def demo_get():
    return {"url": write_container_stl(50, 50, 50, 1)}


@router.post('/shapes')
async def create_shapes():
    # Access header authorization
    authorization_header = request.headers.get('Authorization')

    # Access POST variables
    form_data = await request.form()
    height = form_data.get('height')
    width = form_data.get('width')
    length = form_data.get('length')
    return {"url": write_container_stl(50, 50, 50, 1)}