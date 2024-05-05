from fastapi import FastAPI
from . import models
from .database import engine
from .routes import post
from .routes import user

# create the table
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def homepage():
    return {"message": "Hello World"}

# # IN PATH PARAMETER, DON'T USE ANY WHITESPACE INSIDE CURLY BRACES -> {}
# @app.get("/items/{item_no:int}")
# async def get_item_info(item_no: int):
#     return {"item_id": item_no}

# fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
# @app.get("/items/")
# async def get_items(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]

# @app.get("/file/{filepath:path}")
# async def get_file(filepath):
#     return {"file_path": filepath}

app.include_router(post.route)
app.include_router(user.route)
