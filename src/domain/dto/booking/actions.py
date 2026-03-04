from pydantic import BaseModel


class UnbookAction(BaseModel):
    user_id: str
    model_name: str
