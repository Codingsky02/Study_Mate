from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Text
from db import Base, Engine
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    Targeted_Subject = Column(String(100), nullable=False)
    Class = Column(String(50), nullable=False)
    Previous_Score = Column(String(50), nullable=False)


class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    Subject = Column(String(100), nullable=False)
    Date = Column(String(50), nullable=False)
    Start_time = Column(String(50), nullable=False)
    End_time = Column(String(50), nullable=False)
    Task = Column(String(100), nullable=False)
    Status = Column(String(50), nullable=False)


class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    Subject = Column(String(100), nullable=False)
    Option1 = Column(String(100), nullable=False)
    Answer1 = Column(String(100), nullable=False)
    Option2 = Column(String(100), nullable=False)
    Answer2 = Column(String(100), nullable=False)
    Option3 = Column(String(100), nullable=False)
    Answer3 = Column(String(100), nullable=False)
    Option4 = Column(String(100), nullable=False)
    Answer4 = Column(String(100), nullable=False)



class Explanation(Base):
    __tablename__ = "explanation"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    Subject = Column(String(100), nullable=False)
    Questions = Column(Text, nullable=False)
    Explanation = Column(Text, nullable=False)





class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    subject = Column(String(100), nullable=False)

    due_date = Column(DateTime, nullable=True)

    completed = Column(Boolean, default=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(bind=Engine)





