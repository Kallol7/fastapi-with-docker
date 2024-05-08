from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from copy import deepcopy
from .. import schemas
from .. import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30.0

def create_access_token(data: dict):
    to_encode = deepcopy(data)
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
        
        ## ExpiredSignatureError will work fine without it
        # if datetime.now(timezone.utc).timestamp()>payload.get("exp"):
        #     raise ExpiredSignatureError
        
        token_data = schemas.TokenData(id=id)
        return token_data
    except ExpiredSignatureError:
        credentials_exception.detail = "Token expired. Please log in again."
        raise credentials_exception
    
    except JWTError:
        raise credentials_exception

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    return verify_access_token(token, credentials_exception)
