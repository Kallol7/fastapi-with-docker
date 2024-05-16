from typing import Union, List
from sqlalchemy import Integer, String, Boolean, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Relationship

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, 
        server_default="True"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, 
        server_default=text("now()")
    )
    rating: Mapped[Union[int, None]] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    ##### For Single Element Relationship, Use lazy="joined" #####
    user: Mapped["User"] = Relationship(back_populates="posts", lazy="joined")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone: Mapped[Union[str, None]] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, 
        server_default=text("now()")
    )
    ##### For Collections/List, Use lazy="selectin" #####
    posts: Mapped[List["Post"]] = Relationship(back_populates="user", lazy="selectin")
