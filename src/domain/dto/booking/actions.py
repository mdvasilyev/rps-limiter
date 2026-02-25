from pydantic import BaseModel


class UnbookAction(BaseModel):
    model_name: str
    user_id: str
