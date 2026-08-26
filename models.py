from sqlalchemy import column,integer,string,foreignkey,text
from db import Base

class User(Base):
    __tablename__ = "users"
    id = column(integer,primary_key=True,index=True)
    name = column(string(50),nullable=False)
    email = column(string(100),nullable=False,unique=True)
    password = column(string(100),nullable=False)
    Targeted-Subject = column(string(100),nullable=False)
    Class = column(string(50),nullable=False)
    Previous-Score  = column(string(50),nullable=False)


class Schedule(Base):
    __tablename__ = "schedule"
    id = column(integer,primary_key=True,index=True)
    user_id = column(integer,foreignkey("users.id"),nullable=False)
    Subject = column(string(100),nullable=False)
    Date = column(string(50),nullable=False)
    Start_time = column(string(50),nullable=False)
    End_time = column(string(50),nullable=False)
    Task = column(string(100),nullable=False)
    Status = column(string(50),nullable=False)


class Quiz(Base):
    __tablename__ = "quiz"
    id = column(integer,primary_key=True,index=True)
    user_id = column(integer,foreignkey("users.id"),nullable=False)
    Subject = column(string(100),nullable=False)
    Option1 = column(string(100),nullable=False)
    Answer1 = column(string(100),nullable=False)
    Option2 = column(string(100),nullable=False)
    Answer2 = column(string(100),nullable=False)
    Option3 = column(string(100),nullable=False)
    Answer3 = column(string(100),nullable=False)
    Option4 = column(string(100),nullable=False)
    Answer4 = column(string(100),nullable=False)



class Explanation(Base):
    __tablename__ = "explanation"
    id = column(integer,primary_key=True,index=True)
    user_id = column(integer,foreignkey("users.id"),nullable=False)
    Subject = column(string(100),nullable=False)
    Questions = column(string(100),nullable=False)
    Explanation = column(string(100),nullable=False)






