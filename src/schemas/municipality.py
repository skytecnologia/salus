from pydantic import BaseModel


class Municipality(BaseModel):
    name: str
    external_id: int
