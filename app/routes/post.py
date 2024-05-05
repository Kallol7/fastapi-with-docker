from typing import List
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

route = APIRouter()

# Read All Posts
@route.get("/posts", response_model=List[schemas.PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# Read One Post
@route.get("/posts/{id:int}", response_model=schemas.PostResponse)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")

# Create Post
@route.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_posts(post: schemas.Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the post")

# Update Post
@route.put("/posts/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
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
@route.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
