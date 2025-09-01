from typing import List, Dict, Any

import weaviate
from weaviate.client import WeaviateClient

from models import WeaviateManager
from type_definitions import ContentUUID, TextChunk

class WeaviateCollection:
    """Manages interactions with a specific Weaviate collection for data storage and retrieval."""
    
    def __init__(self) -> None:
        """Initialize the WeaviateCollection instance with collection setup."""
        self.collection_name: str = 'interview_queries'
        self.new_collection: WeaviateManager = WeaviateManager()

        self._create_collection()

        self.client: WeaviateClient = weaviate.connect_to_local()
        self.collection = self.client.collections.get(self.collection_name)
    
    def _create_collection(self) -> None:
        """Create the Weaviate collection if it does not already exist."""
        self.new_collection.create_collection(self.collection_name)

    def import_data(self, data_rows: List[TextChunk]) -> List[ContentUUID]:
        """Import a list of data rows into the Weaviate collection.

        This method uses a fixed-size batching process to efficiently import
        data with a retry mechanism for failed objects.

        Args:
            data_rows: A list of TextChunk dictionaries to be imported.

        Returns:
            A list of ContentUUID dictionaries containing content and UUID pairs.
        """
        content_uuids: List[ContentUUID] = []
        
        with self.collection.batch.fixed_size(batch_size=200) as batch:
            for data_row in data_rows:
                uuid = batch.add_object(properties=data_row)
                data = ContentUUID(
                    content=data_row['text_content'],
                    uuid=str(uuid)
                )
                content_uuids.append(data)
        
        failed_objects = self.collection.batch.failed_objects
        if failed_objects:
            with self.collection.batch.fixed_size(batch_size=50) as failed_batch:
                for data_row in failed_objects:
                    uuid = failed_batch.add_object(properties=data_row)
                    data = ContentUUID(
                        content=str(data_row),
                        uuid=str(uuid)
                    )
                    content_uuids.append(data)
        
        return content_uuids