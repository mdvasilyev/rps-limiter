from pydantic import BaseModel


class WarnUnbookingAction(BaseModel):
    user_id: str
    user_name: str
    model_name: str
