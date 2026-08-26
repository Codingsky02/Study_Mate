from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from os import getenv

load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")

Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=Engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()