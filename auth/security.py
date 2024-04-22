import os
import logging
from typing import Annotated
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import jwt, JWTError
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from models import User, engine

load_dotenv()
logger = logging.getLogger(f"TV_backend.{__name__}")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/security/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(username=username).first()
            return user
    except Exception as e:
        logger.error(f"Error while getting user: {e.__class__.__name__}:{e}")
        return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def is_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


def is_admin(current_user: Annotated[User, Depends(is_user)]):
    if current_user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


class UserPydanticModel(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: Annotated[EmailStr, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=8, max_length=64)]
    name: Annotated[str, Field(min_length=3, max_length=64)]
    phone_number: Annotated[str, Field(min_length=11, max_length=13)]
    type: Annotated[str, Field(min_length=3, max_length=64, default="user")]


class FullUser(UserPydanticModel):
    id: int
