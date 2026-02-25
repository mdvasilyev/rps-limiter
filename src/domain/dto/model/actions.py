from pydantic import BaseModel


class ScaleAction(BaseModel):
    model_id: str
    replicas: int
