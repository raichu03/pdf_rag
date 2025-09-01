from typing import Optional

import weaviate
from weaviate.collections.classes.config import Property, DataType, Configure
from weaviate.client import WeaviateClient


class WeaviateManager:
    """Manages Weaviate collection creation and connection."""
    
    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        """Initialize the Weaviate client.

        Args:
            host: The host address of the Weaviate instance.
            port: The port of the Weaviate instance.
        """
        self.client: WeaviateClient = weaviate.connect_to_local(host=host, port=port)
        self.collection: Optional[object] = None

    def create_collection(self, collection_name: str) -> None:
        """Create a new collection in Weaviate if it doesn't already exist.

        Args:
            collection_name: The name of the collection to create.
        """
        if self.client.collections.exists(collection_name):
            pass
        else:
            try:
                self.collection = self.client.collections.create(
                        name=collection_name,
                        properties=[
                            Property(
                                name="text_content",
                                data_type=DataType.TEXT,
                            )
                        ],
                        vector_config=Configure.Vectors.multi2vec_clip(
                            text_fields=["text_content"],
                            image_fields=None
                        )
                    )
                
            except Exception as e:
                return f"Failed to create collection '{collection_name}': {e}"
    
    def close_connection(self) -> None:
        """Close the Weaviate client connection."""
        if self.client:
            self.client.close()