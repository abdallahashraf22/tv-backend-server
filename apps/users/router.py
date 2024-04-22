from typing import Annotated, Optional

import sqlalchemy
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Response

from models import User, engine
from utils.response import ReturnResponse
from auth import UserPydanticModel, FullUser, is_user, create_access_token, authenticate_user, get_password_hash

users_router = APIRouter(prefix="/security", tags=["security"])


@users_router.post("/register")
def register_user(response: Response, user: UserPydanticModel):
    try:
        with Session(engine) as session:
            new_user = User(
                username=user.username,
                email=user.email,
                password=get_password_hash(user.password),
                name=user.name,
                phone_number=user.phone_number,
                type=user.type,
            )
            session.add(new_user)
            session.commit()
            return ReturnResponse.return_response(
                status_code=status.HTTP_201_CREATED,
                is_success=True,
                data={"id": new_user.id, "email": new_user.email},
            )
    except sqlalchemy.exc.IntegrityError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ReturnResponse.return_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            is_success=False,
            errors=[f"{e.__class__.__name__}: Most probably a duplicate user"],
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ReturnResponse.return_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


class UserUpdate(BaseModel):
    id: int
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: Annotated[EmailStr, Field(min_length=3, max_length=64)]
    name: Annotated[str, Field(min_length=3, max_length=64)]
    old_password: Annotated[str, Field(min_length=8, max_length=64)]
    new_password: Annotated[Optional[str], Field(min_length=8, max_length=64)] = None
    phone_number: Annotated[str, Field(min_length=11, max_length=13)]


@users_router.put("/update")
def update_user(response: Response, user: UserUpdate, current_user: Annotated[FullUser, Depends(is_user)]):
    if current_user.id != user.id or current_user.type != "admin":
        response.status_code = status.HTTP_403_FORBIDDEN.value
        return ReturnResponse.return_response(
            status_code=status.HTTP_403_FORBIDDEN.value,
            is_success=False,
            errors=["You are not allowed to update this user"],
        )
    try:
        with Session(engine) as session:
            user_to_update = session.query(User).filter_by(id=user.id).first()
            if not user_to_update:
                response.status_code = status.HTTP_404_NOT_FOUND
                return ReturnResponse.return_response(
                    status_code=status.HTTP_404_NOT_FOUND,
                    is_success=False,
                    errors=["User not found"],
                )
            if not get_password_hash(user.old_password) == user_to_update.password or current_user.type != "admin":
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return ReturnResponse.return_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    is_success=False,
                    errors=["Incorrect password"],
                )
            user_to_update.username = user.username
            user_to_update.email = user.email
            user_to_update.name = user.name
            user_to_update.phone_number = user.phone_number
            if user.new_password:
                user_to_update.password = get_password_hash(user.new_password)
            session.commit()
            return ReturnResponse.return_response(
                status_code=status.HTTP_200_OK,
                is_success=True,
                data={"id": user_to_update.id, "email": user_to_update.email},
            )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ReturnResponse.return_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


class Token(BaseModel):
    access_token: str
    token_type: str


@users_router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
