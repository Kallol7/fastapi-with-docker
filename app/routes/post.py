# from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .. import models, schemas
from ..database import get_db

route = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# Read All Posts
@route.get("", response_model=List[schemas.PostResponse])
async def get_posts(db: AsyncSession = Depends(get_db)):
    ## For synchronous
    # posts = db.query(models.Post).all()
    
    result = await db.execute(
        select(models.Post)
    )
    posts = result.scalars()
    return posts

# Read One Post
@route.get("/{id:int}", response_model=schemas.PostResponse)
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    ## For synchronous
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    result = await db.execute( 
        select(models.Post).filter(models.Post.id == id)
    )
    post = result.scalar()
    if post:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")

# Create Post
@route.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_posts(post: schemas.Post, db: AsyncSession = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    try:
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the post")

# Update Post
@route.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostUpdate, db: AsyncSession = Depends(get_db)):
    ## For synchronous
    # post_to_update = db.query(models.Post).filter(models.Post.id == id)
    # post_dict = post.model_dump(exclude_unset=True)
    # rowcount = post_to_update.update(post_dict, synchronize_session=False)

    post_dict = post.model_dump(exclude_unset=True)
    statement = update(models.Post).where(models.Post.id == id).values(**post_dict)
    rowcount = (await db.execute(statement)).rowcount

    if rowcount==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")
    try:
        await db.commit()
        # updated_post = post_to_update.first() ## Without async
        updated_post = await db.get(models.Post, id)
        return updated_post
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the post")

# Delete Post
@route.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: AsyncSession = Depends(get_db)):
    ## For synchronous
    # found = db.query(models.Post).filter(models.Post.id == id).first()

    found = await db.get(models.Post, id)

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")

    try:
        await db.delete(found)
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the post")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
