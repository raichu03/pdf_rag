from typing import List, Dict, Any, Optional

from utils import WeaviateCollection, MetaData
from type_definitions import TextChunk, ContentUUID

new_data: MetaData = MetaData()


class AddRecords:
    """Manages the addition of records to both Weaviate and SQL databases."""

    def __init__(self) -> None:
        """Initialize the AddRecords class with instances for Weaviate and SQL operations."""
        self.add_weaviate: WeaviateCollection = WeaviateCollection()
        self.add_sql: MetaData = MetaData()

    def _add_in_weaviate(self, text_data: List[TextChunk]) -> List[ContentUUID]:
        """Import text data into the Weaviate vector database.

        Args:
            text_data: A list of TextChunk dictionaries containing text content to be ingested.

        Returns:
            The response from the Weaviate import operation with UUIDs.
        """
        weaviate_data: List[ContentUUID] = self.add_weaviate.import_data(data_rows=text_data)
        return weaviate_data

    def _add_in_sql(self, document_name: str, text_chunks: List[ContentUUID]) -> Optional[str]:
        """Add text chunks to SQL database.

        Args:
            document_name: The name of the source document.
            text_chunks: A list of ContentUUID entries to be added.
            
        Returns:
            Success or error message from SQL operation.
        """
        sql_data: Optional[str] = new_data.add_data(
            document_name=document_name, 
            text_chunks=text_chunks
        )
        return sql_data
    
    def ingest_data(self, document_name: str, text_chunks: List[str]) -> Optional[str]:
        """Coordinate the complete data ingestion pipeline.

        This method orchestrates the process of adding data to both
        Weaviate and SQL databases.

        Args:
            document_name: The name of the source document.
            text_chunks: A list of text chunks extracted from the document.

        Returns:
            The response from the SQL data insertion.
        """
        all_data: List[TextChunk] = []
        for chunks in text_chunks:
            new_data_dict = TextChunk(text_content=chunks)
            all_data.append(new_data_dict)
        
        weaviate_response: List[ContentUUID] = self._add_in_weaviate(all_data)
        sql_response: Optional[str] = self._add_in_sql(
            document_name=document_name, 
            text_chunks=weaviate_response
        )

        return sql_response