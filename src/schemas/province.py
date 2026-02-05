from pydantic import BaseModel


class Province(BaseModel):
    code: str
    name: str
    external_id: int
