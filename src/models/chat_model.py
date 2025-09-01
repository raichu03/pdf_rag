from typing import Annotated
from pydantic import BaseModel, Field

class ChatModel(BaseModel):
    """Model for chat message requests."""
    
    user_id: Annotated[str, Field(min_length=1, description="Unique identifier for the user")]
    message: Annotated[str, Field(min_length=1, description="The chat message content")]