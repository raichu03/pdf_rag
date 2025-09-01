"""Type definitions for the PDF RAG application."""

from typing import TypedDict, List, Any


class ChatHistoryEntry(TypedDict):
    """Type definition for a single chat history entry."""
    role: str  # "user" or "model"
    parts: str  # The message content


class ChatResponse(TypedDict):
    """Type definition for chat API response."""
    user_id: str
    response: str


class ChatHistoryResponse(TypedDict):
    """Type definition for chat history API response."""
    user_id: str
    history: List[ChatHistoryEntry]


class FunctionResponse(TypedDict):
    """Type definition for function call responses."""
    status: str
    message: str


class InterviewScheduleEntry(TypedDict):
    """Type definition for interview schedule entries."""
    id: int
    candidate_name: str
    candidate_email: str
    interview_date: str
    interview_time: str


class SchedulesResponse(TypedDict):
    """Type definition for schedules API response."""
    status: str
    schedules: List[InterviewScheduleEntry]


class TimeResponse(TypedDict):
    """Type definition for current time response."""
    current_time: str


class DatabaseInfoResponse(TypedDict):
    """Type definition for database information response."""
    status: str
    data: str


class ContentUUID(TypedDict):
    """Type definition for content with UUID."""
    content: str
    uuid: str


class TextChunk(TypedDict):
    """Type definition for text chunks."""
    text_content: str
