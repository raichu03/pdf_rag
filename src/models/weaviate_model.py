import weaviate
from weaviate.collections.classes.config import Property, DataType, Configure

class WeaviateManager:
    """
    Manages Weaviate collection creation and connection.
    """
    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initializes the Weaviate client.

        Args:
            host (str): The host address of the Weaviate instance.
            port (int): The port of the Weaviate instance.
        """
        self.client = weaviate.connect_to_local(host=host, port=port)
        print("Successfully connected to Weaviate client.")

    def create_collection(self, collection_name: str):
        """
        Creates a new collection in Weaviate if it doesn't already exist.

        Args:
            collection_name (str): The name of the collection to create.
            properties (list[Property]): A list of Property objects defining the collection's schema.
        """
        if self.client.collections.exists(collection_name):
            print(f"Collection '{collection_name}' already exists.")
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
                print(f"Collection '{collection_name}' created successfully.")
            except Exception as e:
                print(f"Failed to create collection '{collection_name}': {e}")
    
    def close_connection(self):
        """
        Closes the Weaviate client connection.
        """
        if self.client:
            self.client.close()
            print("Weaviate client connection closed.")
            