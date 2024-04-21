from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean

Base = declarative_base()

# Association Table
user_favorite_content_association = Table(
    "user_favorite_content",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("content_id", Integer, ForeignKey("content.id"), primary_key=True),
)

user_watched_content_association = Table(
    "user_watched_content",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("content_id", Integer, ForeignKey("content.id"), primary_key=True),
)


# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(64))
    name = Column(String(50))
    phone_number = Column(String(13))
    type = Column(String(10), default="user")

    watched_content = relationship(
        "Content",
        secondary=user_watched_content_association,
        back_populates="watched_user",
    )
    favourite_content = relationship(
        "Content",
        secondary=user_favorite_content_association,
        back_populates="favourited_user",
    )
    devices = relationship("Device", back_populates="user")


content_genre_association = Table(
    "content_genre_table",
    Base.metadata,
    Column("genre_id", Integer, ForeignKey("genre.id"), primary_key=True),
    Column("content_id", Integer, ForeignKey("content.id"), primary_key=True),
)


class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    duration = Column(String(8))
    available = Column(Boolean, default=True)

    watched_user = relationship(
        "User",
        secondary=user_watched_content_association,
        back_populates="watched_content",
    )
    favourited_user = relationship(
        "User",
        secondary=user_favorite_content_association,
        back_populates="favourite_content",
    )

    genres = relationship(
        "Genre", secondary=content_genre_association, back_populates="content"
    )


class Genre(Base):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True)

    content = relationship(
        "Content", secondary=content_genre_association, back_populates="genres"
    )


class Device(Base):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mac_address = Column(String(17), unique=True, index=True)
    language = Column(String(2), default="en")
    timezone = Column(String(6), default="UTC")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="devices")
