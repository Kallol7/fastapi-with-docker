# from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas
from ..database import get_db
from ..utils import pwd_context
from .oauth2 import get_current_user

router = APIRouter(
    tags=["Users"]
)

# Create User
@router.post("/users", status_code=status.HTTP_201_CREATED, 
    response_model=schemas.UserResponse, 
    response_model_exclude_none=True)
async def create_account(user: schemas.User, db: AsyncSession = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    new_user.password = pwd_context.hash(user.password)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        print(e)
        await db.rollback()

        if "psycopg.errors.UniqueViolation" in str(e):
            detail_msg = "Email already taken"
            raise HTTPException(status.HTTP_409_CONFLICT, detail=detail_msg)
        else:
            detail_msg = "An error occurred while creating the account"
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_msg)

# Get One User
@router.get("/users/me", response_model=schemas.UserResponse, response_model_exclude_none=True)
async def get_user_profile(db: AsyncSession = Depends(get_db), token_data = Depends(get_current_user)):
    id = token_data.id

    # For synchronous
    # user = db.query(models.User).filter(models.User.id == id).first()

    statement = select(models.User).filter(models.User.id == id)
    result = await db.execute(statement)
    user = result.scalar()
    
    if user:
        return user
    else:
        detail_msg = f"The user with id: {id} was not found"
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=detail_msg)
