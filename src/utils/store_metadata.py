from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import exc

from models import engine, SessionLocal, sql_models

class MetaData:
    """
    A class to handle the ingestion of document data into the database.
    
    This class manages the database session and provides a method
    for adding document chunks.
    """
    def __init__(self):
        """
        Initializes the MetaData class.

        This constructor sets up the necessary database tables by calling
        `create_all` and establishes a new database session for subsequent
        operations.
        """
        sql_models.Base.metadata.create_all(bind=engine)

        self.db : Session = SessionLocal()

    def add_data(self, document_name: str, text_chunks: List[Dict[str, Any]]) -> Optional[List[Dict]]:
        """
        Adds document chunks to the database.

        This method iterates through a list of text chunks, creating a database
        record for each one. Each record is linked to its source document and
        includes its unique chunk ID and text content. The method handles
        database commits and rollbacks to ensure data integrity.

        Args:
            document_name (str): The name of the source document.
            text_chunks (List[Dict[str, Any]]): A list of dictionaries, where each
                                               dictionary contains 'content' and 'uuid'
                                               for a specific text chunk.

        Returns:
            Optional[Dict]: A dictionary with a success message if the data
            is added successfully. Returns None if an SQLAlchemyError occurs
            during the process.
        """
        source_id = document_name

        try:
            for item in text_chunks:
                chunk_str = item['content']
                chunk_id = item['uuid']
                
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
    
    def add_interview(self, name: str, email: str, date: str, time: str):
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