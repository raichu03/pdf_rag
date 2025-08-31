import weaviate
from typing import List

from models import WeaviateManager

class WeaviateCollection:
    """
    Manages interactions with a specific Weaviate collection for data storage and retrieval.

    This class handles the creation and management of a Weaviate collection,
    providing methods to import data efficiently in batches.
    """
    def __init__(self):
        """
        Initializes the WeaviateCollection instance.

        This constructor sets the collection name, initializes the Weaviate
        manager, creates the collection if it doesn't exist, and establishes
        a connection to the local Weaviate instance.
        """
        self.collection_name = 'interview_queries'
        self.new_collection = WeaviateManager()

        self._create_collection()

        self.client = weaviate.connect_to_local()
        self.collection = self.client.collections.get(self.collection_name)
    
    def _create_collection(self):
        """
        Creates the Weaviate collection if it does not already exist.

        This private method uses the `WeaviateManager` to ensure the collection
        is available before any data operations are performed.
        """
        self.new_collection.create_collection(self.collection_name)

    
    def import_data(self, data_rows: List) -> List:
        """
        Imports a list of data rows into the Weaviate collection.

        This method uses a fixed-size batching process to efficiently import
        data. It also includes a retry mechanism for any objects that fail
        during the initial import. The UUIDs and corresponding content of the
        successfully imported objects are returned.

        Args:
            data_rows (List): A list of dictionaries, where each dictionary
                              represents an object to be imported into Weaviate.

        Returns:
            List: A list of dictionaries, each containing the `content` and
                  `uuid` of the successfully imported objects.
        """
        content_uuids = []
        with self.collection.batch.fixed_size(batch_size=200) as batch:
            for data_row in data_rows:
                uuid = batch.add_object(properties=data_row)
                data = {
                    'content': data_row['text_content'],
                    'uuid': str(uuid)
                }
                content_uuids.append(data)
        
        failed_objects = self.collection.batch.failed_objects
        if failed_objects:
            with self.collection.batch.fixed_size(batch_size=50) as failed_batch:
                for data_row in failed_objects:
                    uuid = batch.add_object(properties=data_row)
                    data = {
                        'content': data_row,
                        'uuid': str(uuid)
                    }
                    content_uuids.append(data)
        
        return content_uuids