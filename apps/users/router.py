from typing import Annotated

import sqlalchemy
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Response
from auth.security import authenticate_user, create_access_token, get_password_hash

from models import User, engine
from auth import UserPydanticModel
from utils.response import ReturnResponse

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
