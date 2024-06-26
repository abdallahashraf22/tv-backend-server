import re
from http import HTTPStatus
from typing import Optional, Annotated, List

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Response, Depends

from models import engine, Content, Genre
from utils.response import ReturnResponse
from auth import is_admin, is_user, FullUser

content_router = APIRouter(prefix="/content", tags=["content"])


class ContentBase(BaseModel):
    title: str
    duration: Annotated[
        str, Field(pattern=re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"))
    ]
    available: Optional[bool] = True
    genres: Optional[List[int]] = []


@content_router.get("/")
def get_content(
    response: Response,
    current_user: Annotated[FullUser, Depends(is_user)],
    only_available: bool = False,
):
    try:
        with Session(engine) as session:
            if only_available:
                content = (
                    session.query(Content)
                    .options(joinedload(Content.genres))
                    .filter(Content.available is True)
                    .all()
                )
            else:
                content = (
                    session.query(Content).options(joinedload(Content.genres)).all()
                )
            response.status_code = HTTPStatus.OK.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value, is_success=True, data=content
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@content_router.get("/{content_id}")
def get_content_by_id(
    content_id: int,
    current_user: Annotated[FullUser, Depends(is_user)],
    response: Response,
):
    try:
        with Session(engine) as session:
            content = (
                session.query(Content)
                .options(joinedload(Content.genres))
                .get(content_id)
            )
            if content:
                response.status_code = HTTPStatus.OK.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.OK.value, is_success=True, data=content
                )
            else:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@content_router.post("/")
def create_content(
    content: ContentBase,
    current_user: Annotated[FullUser, Depends(is_admin)],
    response: Response,
):
    content = content.dict()
    genres = content.pop("genres")
    try:
        with Session(engine) as session:
            if genres:
                actual_genres = session.query(Genre).filter(Genre.id.in_(genres)).all()
            if genres and not actual_genres:
                response.status_code = HTTPStatus.BAD_REQUEST.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.BAD_REQUEST.value,
                    is_success=False,
                    errors=["no such genres found"],
                )
            new_content = Content(**content)
            new_content.genres = actual_genres
            session.add(new_content)
            session.commit()
            response.status_code = HTTPStatus.CREATED.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.CREATED.value,
                is_success=True,
                data={"message": "Content created successfully"},
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@content_router.put("/{content_id}")
def update_content(
    content_id: int,
    current_user: Annotated[FullUser, Depends(is_admin)],
    content: ContentBase,
    response: Response,
):
    content = content.dict()
    genres = content.pop("genres")
    try:
        with Session(engine) as session:
            genres = session.query(Genre).filter(Genre.id.in_(genres)).all()
            content_to_update = session.get(Content, content_id)
            if content_to_update:
                for key, value in content.items():
                    setattr(content_to_update, key, value)
                content_to_update.genres = genres
                session.commit()
                response.status_code = HTTPStatus.OK.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.OK.value,
                    is_success=True,
                    data={"message": "Content updated successfully"},
                )
            else:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@content_router.delete("/{content_id}")
def delete_content(
    content_id: int,
    current_user: Annotated[FullUser, Depends(is_admin)],
    response: Response,
):
    try:
        with Session(engine) as session:
            content_to_delete = session.get(Content, content_id)
            if content_to_delete:
                session.delete(content_to_delete)
                session.commit()
                response.status_code = HTTPStatus.OK.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.OK.value,
                    is_success=True,
                    data={"message": "Content deleted successfully"},
                )
            else:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )
