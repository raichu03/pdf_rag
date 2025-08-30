from typing import List, Dict, Optional
import uuid

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
        Initializes the MetaData with a database session.
        
        Args:
            db_session (Session): An active SQLAlchemy database session.
        """
        sql_models.Base.metadata.create_all(bind=engine)

        self.db : Session = SessionLocal()
        self.namespace_uuid = uuid.UUID('264e64d4-ab61-534e-8fff-dcd5a2531ff8')

    def add_data(self, document_name: str, text_chunks: List[str]) -> Optional[List[Dict]]:
        """
        Adds document chunks to the database.

        Generates unique IDs for each chunk based on the document name and
        the first 20 characters of the chunk text.

        Args:
            document_name (str): The name of the source document.
            text_chunks (List[str]): A list of text chunks to be added.

        Returns:
            Optional[List[Dict]]: A list of dictionaries containing the chunk
            text and its UUID, or None if an error occurs.
        """
        source_id = document_name
        added_chunks_info = []

        try:
            for chunk_text in text_chunks:
                chunk_string = source_id + chunk_text[:20]
                chunk_id = str(uuid.uuid5(self.namespace_uuid, chunk_string))
                
                db_chunk = sql_models.DataChunks(
                    sourceId=source_id,
                    chunkID=chunk_id,
                    textChunk=chunk_text
                )
                self.db.add(db_chunk)
                
                added_chunks_info.append({
                    "chunk": chunk_text,
                    "uuid": chunk_id
                })

            self.db.commit()
            print(f"Successfully added {len(text_chunks)} chunks for document '{document_name}'.")
            return added_chunks_info
            
        except exc.SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error adding data: {e}")
            return None