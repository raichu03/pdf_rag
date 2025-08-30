from typing import List

from utils import MetaData
new_data = MetaData()

def ingest_document_chunks(document_name: str, text_chunks: List[str]) -> None:
    """
    Manages the full data ingestion process, including session handling.

    This function acts as a public interface for the module. It handles
    the setup and teardown of the database session, ensuring the process
    is robust and easy to use from other parts of the application.

    Args:
        document_name (str): The name of the source document.
        text_chunks (List[str]): A list of text chunks to be added.
    """

    weaviate_data = new_data.add_data(document_name="sample",text_chunks=text_chunks)

    return weaviate_data