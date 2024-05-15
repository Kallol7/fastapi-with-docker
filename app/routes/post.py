# from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .. import models, schemas
from ..database import get_db
from .oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# Read All Posts
@router.get("", response_model=List[schemas.PostResponse])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    ## For synchronous
    # posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    
    result = await db.execute(
        select(models.Post).where(models.Post.user_id == current_user.id)
    )
    posts = result.scalars()
    return posts

# Read One Post
@router.get("/{id:int}", response_model=schemas.PostResponse)
async def get_post(
    id: int, db: AsyncSession = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    ## For synchronous
    # post = db.query(models.Post).filter(
    #     models.Post.id == id, models.Post.user_id == current_user.id
    # ).first()

    post = (await db.execute(
        select(models.Post).
        where(models.Post.id == id, models.Post.user_id == current_user.id))
    ).scaler()

    if post:
        return post
    else:
        msg = f"The post with id: {id} was not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

# Create Post
@router.post("", status_code=status.HTTP_201_CREATED, 
    response_model=schemas.PostResponse)
async def create_posts(
    post: schemas.Post, db: AsyncSession = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    new_post = models.Post(**post.model_dump())
    new_post.user_id = current_user.id
    try:
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post
    except Exception as e:
        print(e)
        await db.rollback()
        msg = "An error occurred while creating the post"
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)

# Update Post
@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    ## For synchronous
    # post_to_update = db.query(models.Post).filter(
    #     models.Post.id == id, models.Post.user_id == current_user.id
    # )
    # post_dict = post.model_dump(exclude_unset=True)
    # rowcount = post_to_update.update(post_dict, synchronize_session=False)

    post_dict = post.model_dump(exclude_unset=True)
    statement = (
        update(models.Post).
        where(models.Post.id == id, models.Post.user_id == current_user.id).
        values(**post_dict)
    )
    rowcount = (await db.execute(statement)).rowcount

    if rowcount==0:
        msg = f"The post with id: {id} was not found"
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=msg)
    try:
        await db.commit()
        # updated_post = post_to_update.first() ## Without async
        updated_post = await db.get(models.Post, id)
        return updated_post
    except Exception as e:
        await db.rollback()
        msg = "An error occurred while updating the post"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)

# Delete Post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int, db: AsyncSession = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    ## For synchronous
    # found = db.query(models.Post).filter(
    #     models.Post.id == id, models.Post.user_id == current_user.id
    # ).first()

    found = await db.get(models.Post, id)

    if not found or found.user_id != current_user.id:
        msg = f"The post with id: {id} was not found"
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=msg)

    try:
        await db.delete(found)
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        msg = "An error occurred while deleting the post"
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
