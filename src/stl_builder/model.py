from pydantic import BaseModel


class Msg(BaseModel):
    msg: str


class SimpleBox(BaseModel):
    length: float
    width: float
    height: float


class SimpleBox2(BaseModel):
    length: float
    width: float
    height: float
    thickness: float


class ShapeData(BaseModel):
    shape: str
    meta_data: SimpleBox | SimpleBox2
