from sqlalchemy import Column, Integer, String
from .sql_database import Base

class DataChunks(Base):
    __tablename__="TextChunk"

    id = Column(Integer, primary_key=True, index=True)
    sourceId = Column(String(100), nullable=False)
    chunkID = Column(String, nullable=False)
    textChunk = Column(String, nullable=False)

    def __repr__(self):
        return f"<DataChunks(id={self.id}, source_id='{self.source_id}', chunk_id={self.chunk_id})>"