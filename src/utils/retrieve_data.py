from sqlalchemy.orm import Session
from sqlalchemy import exc

from models import engine, SessionLocal, sql_models

sql_models.Base.metadata.create_all(bind=engine)

class SqlData:
    """
    A class to handle database operations using SQLAlchemy.
    """
    
    def __init__(self):
        """
        Initializes a new database session.
        """
        self.db: Session = SessionLocal()

    def get_interview_data(self):
        """
        Retrieves all data chunks from the database.

        Returns:
            list: A list of all DataChunks objects.
        """
        return self.db.query(sql_models.DataInterview).all()

    def get_chunk_data(self, chunk_id: str):
        """
        Retrieves a single data chunk by its ID.

        Args:
            chunk_id (int): The ID of the data chunk to retrieve.

        Returns:
            sql_models.DataChunks: The DataChunks object with the specified ID, or None if not found.
        """
        return self.db.query(sql_models.DataChunks).filter(sql_models.DataChunks.chunkID == chunk_id).first()

    def close(self):
        """
        Closes the database session.
        """
        self.db.close()