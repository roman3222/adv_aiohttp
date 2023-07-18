import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
port = os.getenv('PG_PORT')
db_name = os.getenv('PG_DB')

DSN = f'postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}'
engine = create_async_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True)
    creation_time = Column(DateTime, server_default=func.now())
    advertisements = relationship("Advertisement")


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    descriptions = Column(String, nullable=False)
    creations_date = Column(DateTime, server_default=func.now())
    user_id = Column(ForeignKey("users.id"), nullable=True)


