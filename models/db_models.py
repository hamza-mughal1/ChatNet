from models.database_orm import Base
from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    user_name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    bio = Column(String, server_default="None")
    profile_pic = Column(String, server_default="None")
    created_at = Column(DateTime, server_default=func.now())

    posts = relationship("Posts", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comments", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Likes", back_populates="user", cascade="all, delete-orphan")
    access_token = relationship("AccessToken", back_populates="user", cascade="all, delete-orphan")
    refresh_token = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    following = relationship("Follows", foreign_keys="[Follows.follower_id]", back_populates="follower", cascade="all, delete-orphan")
    followers = relationship("Follows", foreign_keys="[Follows.following_id]", back_populates="following", cascade="all, delete-orphan")


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Likes", back_populates="post", cascade="all, delete-orphan")


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("Users", back_populates="comments")
    post = relationship("Posts", back_populates="comments")


class Follows(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    follower_id = Column(Integer, ForeignKey('users.id'))
    following_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())

    follower = relationship("Users", foreign_keys=[follower_id], back_populates="following")
    following = relationship("Users", foreign_keys=[following_id], back_populates="followers")

class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    created_at = Column(DateTime, server_default=func.now()) 

    user = relationship("Users", back_populates="likes")
    post = relationship("Posts", back_populates="likes")

class AccessToken(Base):
    __tablename__ = "access_token"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now()) 

    user = relationship("Users", back_populates="access_token")
    refresh_token = relationship("RefreshToken", back_populates="access_token", cascade="all, delete-orphan")

class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    access_token_id = Column(Integer, ForeignKey('access_token.id'))
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now()) 

    user = relationship("Users", back_populates="refresh_token")
    access_token = relationship("AccessToken", back_populates="refresh_token")