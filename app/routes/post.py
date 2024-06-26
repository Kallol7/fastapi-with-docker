# from sqlalchemy.orm import Session
from typing import List, Union
from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from .. import models, schemas
from ..database import get_db
from .oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# Read All Public Posts
@router.get("/public", response_model=List[schemas.PostResponsePublic])
async def get_public_posts(db: AsyncSession = Depends(get_db), 
    limit: int = 5, skip: int = 0, search: Union[str, None] = None
):
    ## For synchronous
    # posts = db.query(models.Post).filter(models.Post.published == True).all()

    limit = min(limit, 100)

    if search and search.strip():
        statement = (select(models.Post).where(
            models.Post.published == True, models.Post.content.contains(search)
        ).limit(limit).offset(skip))
    else :
        statement = (select(models.Post).where(
            models.Post.published == True
        ).limit(limit).offset(skip))

    try:
        posts = (await db.execute(statement)).scalars().all()
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if posts:
        return posts

    raise HTTPException(status.HTTP_404_NOT_FOUND)

# Read All Public Posts, With Pagination
@router.get("/public/page/{page_no:int}", response_model=List[schemas.PostResponsePublic])
async def get_public_posts_paginated(db: AsyncSession = Depends(get_db),
    page_no: int = 0
):
    page_no = max(page_no, 0)
    limit = 5
    skip = page_no * limit

    try:
        statement = select(models.Post).limit(limit).offset(skip)
        posts = (await db.execute(statement)).scalars().all()
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if posts:
        return posts

    raise HTTPException(status.HTTP_404_NOT_FOUND)

# Read All Posts Created By User, Requires Login
@router.get("", response_model=List[schemas.PostResponse])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    ## For synchronous
    # posts = db.query(models.Post).filter(
    #     models.Post.user_id == current_user.id
    # ).all()

    posts = (await db.execute(
        select(models.Post).
        where(models.Post.user_id == current_user.id))
    ).scalars()

    return posts

# Read One Post Created By User, Requires Login
@router.get("/{id:int}", response_model=schemas.PostResponseSingle)
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
    ).scalar()

    if post:
        return post
    else:
        msg = f"The post with id: {id} was not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

# Create A Post, Requires Login
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

# Update A Post, Requires Login
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

# Delete A Post, Requires Login
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
