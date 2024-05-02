from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

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

# Read All Posts
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

# Read One Post
@app.get("/posts/{id:int}")
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")

# Create Post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: schemas.Post, db: Session = Depends(get_db)):
    new_post = models.Post(title=post.title, content=post.content, published=post.published)
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return {"message": "Post has been created", "data": new_post}
    except Exception as e:
        print(e)
        db.rollback()
        return {"message": "Something went wrong", "data": None}

# Update Post
@app.put("/posts/{id}")
async def update_post(id: int, post: schemas.Post, db: Session = Depends(get_db)):
    post_to_update = db.query(models.Post).filter(models.Post.id == id)
    post_dict = post.model_dump(exclude_unset=True)
    rowcount = post_to_update.update(post_dict, synchronize_session=False)

    if rowcount==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")
    
    try:
        db.commit()
        updated_post = post_to_update.first()
        return updated_post
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the post")

# Delete Post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    found = db.query(models.Post).filter(models.Post.id == id).first()

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")

    try:
        db.delete(found)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the post")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
