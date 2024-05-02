from typing import Union
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    published: Mapped[bool] = mapped_column(Boolean, default=True)
    username: Mapped[Union[str, None]] = mapped_column(String, default=None)
    rating: Mapped[Union[int, None]] = mapped_column(Integer, nullable=True, default=None)

    class Config:
        orm_mode = True
