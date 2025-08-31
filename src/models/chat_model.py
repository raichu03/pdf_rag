from pydantic import BaseModel

class ChatModel(BaseModel):
    user_id: str
    message: str