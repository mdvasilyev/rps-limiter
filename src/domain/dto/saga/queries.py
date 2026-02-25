from pydantic import BaseModel


class SagaQuery(BaseModel):
    saga_id: str
