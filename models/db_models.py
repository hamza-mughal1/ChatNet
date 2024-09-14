from models.database_orm import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime, text
from sqlalchemy.orm import relationship
from utilities.settings import setting

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(300), nullable=False)
    user_name = Column(String(300), nullable=False, unique=True)
    email = Column(String(300), nullable=False, unique=True)
    password = Column(String(300), nullable=False)
    bio = Column(String(300), server_default="None")
    profile_pic = Column(String(300), server_default="None")
    created_at = Column(DateTime, server_default=func.now())

    posts = relationship("Posts", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comments", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Likes", back_populates="user", cascade="all, delete-orphan")
    access_token = relationship("AccessTokens", back_populates="user", cascade="all, delete-orphan")
    refresh_token = relationship("RefreshTokens", back_populates="user", cascade="all, delete-orphan")
    following = relationship("Follows", foreign_keys="[Follows.follower_id]", back_populates="follower", cascade="all, delete-orphan")
    followers = relationship("Follows", foreign_keys="[Follows.following_id]", back_populates="following", cascade="all, delete-orphan")


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(300), nullable=False)
    content = Column(String(300), nullable=False)
    image = Column(String(300), server_default="None")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Likes", back_populates="post", cascade="all, delete-orphan")


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String(300), nullable=False)
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

class AccessTokens(Base):
    __tablename__ = "access_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(300), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now()) 

    user = relationship("Users", back_populates="access_token")
    refresh_token = relationship("RefreshTokens", back_populates="access_token", cascade="all, delete-orphan")

class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    access_token_id = Column(Integer, ForeignKey('access_tokens.id'))
    token = Column(String(300), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now()) 

    user = relationship("Users", back_populates="refresh_token")
    access_token = relationship("AccessTokens", back_populates="refresh_token")


def create_refresh_and_access_token_deletion_events(engine):
    QUERY = f"""SET GLOBAL event_scheduler = ON;

                CREATE EVENT IF NOT EXISTS delete_exp_acess_tokens
                ON SCHEDULE EVERY 30 MINUTE
                DO
                DELETE FROM access_tokens
                WHERE created_at < NOW() - INTERVAL {setting.refresh_token_expire_minutes} MINUTE;

                CREATE EVENT IF NOT EXISTS delete_exp_refresh_tokens
                ON SCHEDULE EVERY 30 MINUTE
                DO
                DELETE FROM refresh_tokens
                WHERE created_at < NOW() - INTERVAL {setting.refresh_token_expire_minutes} MINUTE;""" 


    with engine.connect() as connection:
        connection.execute(text(QUERY))


if setting.db == "mysql":
    create_refresh_and_access_token_deletion_events(engine)