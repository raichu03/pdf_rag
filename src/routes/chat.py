from typing import Literal
import json

from redis import Redis
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Depends

from models import ChatModel
from services import ChatRag

router = APIRouter()
gemini_client = ChatRag()

def get_redis_client():
    """
    Creates a Redis client connection and yields it.
    The 'yield' keyword ensures the connection is closed after the request is completed.
    """
    redis_client = Redis(host='localhost', port=6379, db=0)
    try:
        yield redis_client
    finally:
        redis_client.close()

@router.post(
    "/chat",
    summary="Chat with the LLM",
    description=""" RAG based chat system with the uploaded file, make smart .
    """,
    status_code=status.HTTP_201_CREATED,
)
async def chat_rag(
    chat_message: ChatModel,
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Handles a user's chat message, retrieves the conversation history from Redis,
    and returns a simulated machine response.
    """
    user_id = chat_message.user_id
    user_message = chat_message.message

    conversation_key = f"chat_history:{user_id}"

    history_bytes = redis_client.get(conversation_key)
    
    if history_bytes:
        try:
            history = json.loads(history_bytes)
        except json.JSONDecodeError:
            history = []
    else:
        history = []
    
    print(history)
    print(type(history))
    machine_response = gemini_client.conversation(user_input=user_message, chat_history=history)

    history.append({"role": "user", "parts": user_message})

    history.append({"role": "model", "parts": machine_response})

    redis_client.set(conversation_key, json.dumps(history))

    return {"user_id": user_id, "response": machine_response}


@router.post(
    "/chat-history",
    summary="Chat with the LLM",
    description=""" RAG based chat system with the uploaded file, make smart .
    """,
    status_code=status.HTTP_201_CREATED,
)
async def get_history(user_id: str, redis_client: Redis = Depends(get_redis_client)):
    """
    Retrieves and returns the full conversation history for a given user ID.
    """
    conversation_key = f"chat_history:{user_id}"
    history_bytes = redis_client.get(conversation_key)

    if not history_bytes:
        raise HTTPException(status_code=404, detail="No chat history found for this user.")
    
    history = json.loads(history_bytes)
    return {"user_id": user_id, "history": history}