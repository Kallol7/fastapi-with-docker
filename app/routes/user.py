from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..utils import pwd_context

route = APIRouter()

# Create User
@route.post("/users", status_code=status.HTTP_201_CREATED, 
    response_model=schemas.UserResponse, 
    response_model_exclude_none=True)
async def create_posts(user: schemas.User, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    new_user.password = pwd_context.hash(user.password)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        print(e)
        db.rollback()

        if "psycopg.errors.UniqueViolation" in str(e):
            detail_msg = "Email already taken"
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail_msg)
        else:
            detail_msg = "An error occurred while creating the account"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_msg)

# Get One User
@route.get("/users/{id:int}", response_model=schemas.UserResponse,
    response_model_exclude_none=True)
async def get_post(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The user with id: {id} was not found"
        )
