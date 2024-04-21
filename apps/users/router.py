from typing import Annotated

from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from auth.security import authenticate_user, create_access_token

from models import User, engine
from utils.response import ReturnResponse

security_router = APIRouter(prefix="/security", tags=["security"])


class UserPydanticModel(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: Annotated[EmailStr, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=8, max_length=64)]
    name: Annotated[str, Field(min_length=3, max_length=64)]
    phone: Annotated[str, Field(min_length=13, max_length=13)]
    type: Annotated[str, Field(min_length=3, max_length=64, default="user")]


@security_router.post("/register")
def register_user(user: UserPydanticModel):
    try:
        with Session(engine) as session:
            new_user = User(
                username=user.username,
                email=user.email,
                password=user.password,
                name=user.name,
                phone=user.phone,
                type=user.type
            )
            session.add(new_user)
            session.commit()
            return ReturnResponse.return_response(
                status_code=status.HTTP_201_CREATED,
                is_success=True,
                data={"id": new_user.id, "email": new_user.email}
            )
    except Exception as e:
        return ReturnResponse.return_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"]
        )


class Token(BaseModel):
    access_token: str
    token_type: str


@security_router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
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
