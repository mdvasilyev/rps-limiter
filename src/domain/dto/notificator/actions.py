from pydantic import BaseModel


class WarnUnbookingAction(BaseModel):
    user_id: str
    model_name: str
