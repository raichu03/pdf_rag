from typing import Optional

from sqlalchemy import Column, Integer, String
from .sql_database import Base

class DataChunks(Base):
    """SQLAlchemy model for storing text chunks and their metadata."""
    
    __tablename__ = "TextChunk"

    id: int = Column(Integer, primary_key=True, index=True)
    sourceId: str = Column(String(100), nullable=False)
    chunkID: str = Column(String, nullable=False)
    textChunk: str = Column(String, nullable=False)

    def __repr__(self) -> str:
        """String representation of the DataChunks instance."""
        return f"textChunk={self.textChunk}, source_id='{self.sourceId}', chunk_id={self.chunkID}"


class DataInterview(Base):
    """SQLAlchemy model for storing interview scheduling information."""
    
    __tablename__ = "Meetings"

    id: int = Column(Integer, primary_key=True, index=True)
    candidate_name: str = Column(String(100), nullable=False)
    candidate_email: str = Column(String, nullable=False)
    interview_date: str = Column(String, nullable=False)
    interview_time: str = Column(String, nullable=False)

    def __repr__(self) -> str:
        """String representation of the DataInterview instance."""
        return (
            f"candidate_name='{self.candidate_name}', date={self.interview_date}, "
            f"interview_time={self.interview_time}, candidate_email={self.candidate_email}"
        )