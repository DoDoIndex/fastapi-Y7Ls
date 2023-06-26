from fastapi import APIRouter, HTTPException, status

from .services.shapes.simple_box import create_shape as create_simple_box
from .services.shapes.simple_box_with_lid import create_shape as simple_box_with_lid

from .model import ShapeData

router = APIRouter(prefix="/v1")


@router.get("/")
async def homepage() -> str:
    return {"value": "hello world"}


@router.get("/test")
async def demo_get():
    return {"url": create_simple_box(30, 10, 50, 1)}


@router.post("/shapes")
async def create_shapes(data: ShapeData):
    if data.shape == "simple_box":
        length = data.meta_data.length
        width = data.meta_data.width
        height = data.meta_data.height
        thickness = data.meta_data.thickness
        return create_simple_box(length, width, height, thickness)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=[{"msg": "invalid shape"}]
        )
