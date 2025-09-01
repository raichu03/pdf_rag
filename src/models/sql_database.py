from typing import Type

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

SQLALCHEMY_DATABASE_URL: str = "sqlite:///./metadata.db"

engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal: Type[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base: DeclarativeMeta = declarative_base()