# from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas
from ..database import get_db
from ..utils import pwd_context

route = APIRouter(
    tags=["Users"]
)

# Create User
@route.post("/users", status_code=status.HTTP_201_CREATED, 
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
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail_msg)
        else:
            detail_msg = "An error occurred while creating the account"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_msg)

# Get One User
@route.get("/users/{id:int}", response_model=schemas.UserResponse,
    response_model_exclude_none=True)
async def get_user_info(id: int, db: AsyncSession = Depends(get_db)):
    ## For synchronous
    # user = db.query(models.User).filter(models.User.id == id).first()

    statement = select(models.User).filter(models.User.id == id)
    result = await db.execute(statement)
    user = result.scalar()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The user with id: {id} was not found"
        )
