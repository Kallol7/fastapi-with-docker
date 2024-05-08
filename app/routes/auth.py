from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas
from ..database import get_db
from ..utils import pwd_context
from .oauth2 import create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email==form_data.username))
    user = result.scalar()

    if not user: # user doesn't exist, but don't give too much information
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong Username or Password")
    
    if not pwd_context.verify(secret=form_data.password, hash=user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong Username or Password")
    
    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
