from typing import List, Dict, Any

from utils import WeaviateCollection

from utils import MetaData
new_data = MetaData()

class AddRecords:
    """
    Manages the addition of records to both Weaviate and SQL databases.

    This class provides a comprehensive solution for data ingestion,
    handling the transformation and storage of data across a vector
    database (Weaviate) and a relational database (SQL).
    """

    def __init__(self):
        """
        Initializes the AddRecords class with instances for Weaviate and SQL operations.
        """
        self.add_weaviate = WeaviateCollection()
        self.add_sql = MetaData()

    def _add_in_weaviate(self, text_data: List[Dict[str, Any]]):
        """
        Imports text data into the Weaviate vector database.

        Args:
            text_data (List[Dict[str, Any]]): A list of dictionaries, where each
                                               dictionary contains the text content
                                               to be ingested.

        Returns:
            The response from the Weaviate import operation, typically including
            the status and UUIDs of the imported objects.
        """
        weaviate_data = self.add_weaviate.import_data(data_rows=text_data)

        return weaviate_data

    def _add_in_sql(self, document_name: str, text_chunks: List[Dict[str, Any]]) -> None:
        """
        Manages the full data ingestion process, including session handling.

        This function acts as a public interface for the module. It handles
        the setup and teardown of the database session, ensuring the process
        is robust and easy to use from other parts of the application.

        Args:
            document_name (str): The name of the source document.
            text_chunks (List[str]): A list of text chunks to be added.
        """

        sql_data = new_data.add_data(document_name=document_name,text_chunks=text_chunks)

        return sql_data
    
    def ingest_data(self, document_name: str, text_chunks: List[str]):
        """
        Coordinates the complete data ingestion pipeline.

        This method orchestrates the process of adding data to both
        Weaviate and SQL databases. It prepares the data for Weaviate,
        calls the internal methods to add records to each database, and
        returns the final response from the SQL operation.

        Args:
            document_name (str): The name of the source document.
            text_chunks (List[str]): A list of text chunks extracted from the document.

        Returns:
            The response from the SQL data insertion, indicating the success
            or failure of the operation.
        """
        
        all_data = []
        for chunks in text_chunks:
            new_data = {
                'text_content': chunks
            }

            all_data.append(new_data)
        
        weaviate_response = self._add_in_weaviate(all_data)

        sql_resonse = self._add_in_sql(document_name=document_name, text_chunks=weaviate_response)

        return sql_resonse