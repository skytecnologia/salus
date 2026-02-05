from pydantic import BaseModel


class Insurer(BaseModel):
    name: str
    external_id: int
