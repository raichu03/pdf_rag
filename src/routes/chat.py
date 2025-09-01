from typing import List, Dict, Any, Generator
import json

from redis import Redis
from fastapi import APIRouter, HTTPException, status, Depends

from models import ChatModel
from services import ChatRag
from type_definitions import ChatResponse, ChatHistoryResponse, ChatHistoryEntry

router: APIRouter = APIRouter()
gemini_client: ChatRag = ChatRag()

def get_redis_client() -> Generator[Redis, None, None]:
    """Create a Redis client connection and yield it.
    
    The 'yield' keyword ensures the connection is closed after the request is completed.
    
    Yields:
        Redis client instance.
    """
    redis_client: Redis = Redis(host='localhost', port=6379, db=0)
    try:
        yield redis_client
    finally:
        redis_client.close()


@router.post(
    "/chat",
    summary="Chat with the LLM",
    description="RAG based chat system with the uploaded file, make smart.",
    status_code=status.HTTP_201_CREATED,
)
async def chat_rag(
    chat_message: ChatModel,
    redis_client: Redis = Depends(get_redis_client)
) -> ChatResponse:
    """Handle a user's chat message and return the model's response.
    
    Args:
        chat_message: The chat message containing user_id and message.
        redis_client: Redis client for conversation history storage.
        
    Returns:
        Dictionary containing user_id and response.
    """
    user_id: str = chat_message.user_id
    user_message: str = chat_message.message

    conversation_key: str = f"chat_history:{user_id}"
    history_bytes = redis_client.get(conversation_key)
    
    history: List[ChatHistoryEntry]
    if history_bytes:
        try:
            history_data = json.loads(history_bytes)
            history = [ChatHistoryEntry(role=item["role"], parts=item["parts"]) for item in history_data]
        except json.JSONDecodeError:
            history = []
    else:
        history = []
    
    machine_response: str = gemini_client.conversation(
        user_input=user_message, 
        chat_history=history
    )

    new_user_entry = ChatHistoryEntry(role="user", parts=user_message)
    new_model_entry = ChatHistoryEntry(role="model", parts=machine_response)
    
    history.append(new_user_entry)
    history.append(new_model_entry)

    redis_client.set(conversation_key, json.dumps([dict(entry) for entry in history]))

    return ChatResponse(user_id=user_id, response=machine_response)


@router.post(
    "/chat-history",
    summary="Get chat history",
    description="Retrieve the full conversation history for a given user ID.",
    status_code=status.HTTP_200_OK,
)
async def get_history(
    user_id: str, 
    redis_client: Redis = Depends(get_redis_client)
) -> ChatHistoryResponse:
    """Retrieve and return the full conversation history for a given user ID.
    
    Args:
        user_id: The user's unique identifier.
        redis_client: Redis client for conversation history retrieval.
        
    Returns:
        Dictionary containing user_id and conversation history.
        
    Raises:
        HTTPException: If no chat history is found for the user.
    """
    conversation_key: str = f"chat_history:{user_id}"
    history_bytes = redis_client.get(conversation_key)

    if not history_bytes:
        raise HTTPException(
            status_code=404, 
            detail="No chat history found for this user."
        )
    
    history_data = json.loads(history_bytes)
    history: List[ChatHistoryEntry] = [
        ChatHistoryEntry(role=item["role"], parts=item["parts"]) 
        for item in history_data
    ]
    
    return ChatHistoryResponse(user_id=user_id, history=history)