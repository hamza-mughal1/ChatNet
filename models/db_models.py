from models.database_orm import Base
from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    user_name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, server_default="0")
    created_at = Column(DateTime, server_default=func.now())


class Profiles(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    bio = Column(String, nullable=False)
    profile_pic = Column(String, server_default="None")
    created_at = Column(DateTime, server_default=func.now())

class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Follows(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    follower_id = Column(Integer, ForeignKey('users.id'))
    following_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())
