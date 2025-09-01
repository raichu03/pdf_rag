from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import exc
import weaviate
from weaviate.client import WeaviateClient

from models import engine, SessionLocal, sql_models

sql_models.Base.metadata.create_all(bind=engine)


class SqlData:
    """A class to handle database operations using SQLAlchemy."""
    
    def __init__(self) -> None:
        """Initialize a new database session and Weaviate client."""
        self.db: Session = SessionLocal()
        self.client: WeaviateClient = weaviate.connect_to_local()
        self.collection = self.client.collections.get('interview_queries')

    def get_interview_data(self) -> List[sql_models.DataInterview]:
        """Retrieve all interview data from the database.

        Returns:
            A list of all DataInterview objects.
        """
        return self.db.query(sql_models.DataInterview).all()

    def get_chunk_data(self, chunk_id: str) -> Optional[sql_models.DataChunks]:
        """Retrieve a single data chunk by its ID.

        Args:
            chunk_id: The ID of the data chunk to retrieve.

        Returns:
            The DataChunks object with the specified ID, or None if not found.
        """
        return self.db.query(sql_models.DataChunks).filter(
            sql_models.DataChunks.chunkID == chunk_id
        ).first()

    def close(self) -> None:
        """Close the database session."""
        self.db.close()

    def _weaviate_data(self, user_query: str) -> List[str]:
        """Retrieve relevant UUIDs from Weaviate based on the user query.
        
        Args:
            user_query: The query to search for.
            
        Returns:
            List of UUIDs for relevant documents.
        """
        all_responses = self.collection.query.hybrid(
            query=user_query,
            limit=10,
        )
        all_uuid: List[str] = []
        for responses in all_responses.objects:
            uuid_string: str = str(responses.uuid)
            all_uuid.append(uuid_string)

        return all_uuid
    
    def all_context(self, query: str) -> str:
        """Retrieve all relevant context for a given query.
        
        Args:
            query: The search query.
            
        Returns:
            Concatenated text content from relevant chunks.
        """
        weaviate_uuid: List[str] = self._weaviate_data(user_query=query)

        context_list: List[str] = []
        for uuid in weaviate_uuid:
            meta_data: Optional[sql_models.DataChunks] = self.get_chunk_data(chunk_id=uuid)

            if meta_data is None:
                continue
            else:
                context_list.append(meta_data.textChunk)
        
        total_context: str = "".join(context_list)
        return total_context