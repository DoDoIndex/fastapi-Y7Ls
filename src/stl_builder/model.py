from pydantic import BaseModel


class Msg(BaseModel):
    msg: str


class SimpleBox(BaseModel):
    length: float
    width: float
    height: float
    thickness: float


class SimpleBoxWithLid(BaseModel):
    length: float
    width: float
    height: float
    thickness: float


class ShapeData(BaseModel):
    shape: str
    meta_data: SimpleBox | SimpleBoxWithLid
