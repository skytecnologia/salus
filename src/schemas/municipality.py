from pydantic import BaseModel


class Municipality(BaseModel):
    code: str
    name: str
    external_id: int
