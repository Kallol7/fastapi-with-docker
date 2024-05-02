from typing import Union
from pydantic import BaseModel

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    username: Union[str, None] = None
    rating: Union[int, None] = None
