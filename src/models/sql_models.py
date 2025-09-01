from sqlalchemy import Column, Integer, String
from .sql_database import Base

class DataChunks(Base):
    __tablename__="TextChunk"

    id = Column(Integer, primary_key=True, index=True)
    sourceId = Column(String(100), nullable=False)
    chunkID = Column(String, nullable=False)
    textChunk = Column(String, nullable=False)

    def __repr__(self):
        return f"textChunk={self.textChunk}, source_id='{self.sourceId}', chunk_id={self.chunkID}"
    
class DataInterview(Base):
    __tablename__="Meetings"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(100), nullable=False)
    candidate_email = Column(String, nullable=False)
    interview_date = Column(String, nullable=False)
    interview_time = Column(String, nullable=False)

    def __repr__(self):
        return f"candidate_name='{self.candidate_name}', date={self.interview_date}, interview_time={self.interview_time}, candidate_email={self.candidate_email}"