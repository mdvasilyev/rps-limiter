from pydantic import BaseModel


class Scale(BaseModel):
    model_id: str
    replicas: int
