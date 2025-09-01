from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import exc

from models import engine, SessionLocal, sql_models
from type_definitions import ContentUUID

class MetaData:
    """A class to handle the ingestion of document data into the database."""
    
    def __init__(self) -> None:
        """Initialize the MetaData class with database tables and session."""
        sql_models.Base.metadata.create_all(bind=engine)
        self.db: Session = SessionLocal()

    def add_data(self, document_name: str, text_chunks: List[ContentUUID]) -> Optional[str]:
        """Add document chunks to the database.

        Args:
            document_name: The name of the source document.
            text_chunks: A list of ContentUUID dictionaries containing 'content' and 'uuid' 
                        for each text chunk.

        Returns:
            Success message if data is added successfully, error message otherwise.
        """
        source_id: str = document_name

        try:
            for item in text_chunks:
                chunk_str: str = item['content']
                chunk_id: str = item['uuid']
                
                db_chunk = sql_models.DataChunks(
                    sourceId=source_id,
                    chunkID=chunk_id,
                    textChunk=chunk_str
                )
                self.db.add(db_chunk)

            self.db.commit()
            return f"Successfully added {len(text_chunks)} chunks for document '{document_name}'."

        except exc.SQLAlchemyError as e:
            self.db.rollback()
            return f"Error adding data: {e}"
    
    def add_interview(self, name: str, email: str, date: str, time: str) -> Optional[str]:
        """Add interview scheduling information to the database.
        
        Args:
            name: Candidate's name.
            email: Candidate's email.
            date: Interview date.
            time: Interview time.
            
        Returns:
            Success message if interview is added successfully, error message otherwise.
        """
        try:
            db_chunk = sql_models.DataInterview(
                candidate_name=name,
                candidate_email=email,
                interview_date=date,
                interview_time=time
            )
            self.db.add(db_chunk)
            self.db.commit()
            return f"Successfully added Interview for {name} has been booked for {date} at {time}."

        except exc.SQLAlchemyError as e:
            self.db.rollback()
            return f"Error adding data: {e}"