from pydantic import BaseModel


class Province(BaseModel):
    name: str
    external_id: int
