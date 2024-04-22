from http import HTTPStatus
from typing import Annotated

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Response

from auth import is_user, FullUser
from utils.response import ReturnResponse
from models import User, Content, engine, Session

actions_router = APIRouter(prefix="/actions", tags=["actions"])


class ContentId(BaseModel):
    content_id: int


@actions_router.get("/watch")
def get_user_watched(current_user: Annotated[FullUser, Depends(is_user)], response: Response):
    try:
        with Session(engine) as session:
            user = session.get(User, current_user.id)
            watched_content = user.watched_content
            response.status_code = HTTPStatus.OK.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data=[content for content in watched_content],
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@actions_router.post("/watch")
def user_watched_content(current_user: Annotated[FullUser, Depends(is_user)], content: ContentId, response: Response):
    try:
        with Session(engine) as session:
            user = session.get(User, current_user.id)
            content = session.query(Content).filter_by(id=content.content_id).first()
            if not content:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
            user.watched_content.append(content)
            session.commit()
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data={"user_id": user.id, "content_id": content.id},
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@actions_router.delete("/watch")
def user_watched_content(current_user: Annotated[FullUser, Depends(is_user)], content: ContentId, response: Response):
    try:
        with Session(engine) as session:
            user = session.get(User, current_user.id)
            content = session.query(Content).filter_by(id=content.content_id).first()
            if not content:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
            user.watched_content.remove(content)
            session.commit()
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data={"Message": "unwatched successfully"},
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@actions_router.get("/favourites")
def get_user_favourites(current_user: Annotated[FullUser, Depends(is_user)], response: Response):
    try:
        with Session(engine) as session:
            user = session.get(User, current_user.id)
            favourite_content = user.favourite_content
            response.status_code = HTTPStatus.OK.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data=[content.id for content in favourite_content],
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@actions_router.post("/favourites")
def user_favourites_content(current_user: Annotated[FullUser, Depends(is_user)], content: ContentId,
                            response: Response):
    try:
        with Session(engine) as session:
            user = session.get(User, current_user.id)
            content = session.query(Content).filter_by(id=content.content_id).first()
            if not content:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
            user.favourite_content.append(content)
            session.commit()
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data={"user_id": user.id, "content_id": content.id},
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@actions_router.delete("/favourites")
def user_favourites_content(current_user: Annotated[FullUser, Depends(is_user)], content: ContentId,
                            response: Response):
    try:
        with Session(engine) as session:
            user = session.get(User, current_user.id)
            content = session.query(Content).filter_by(id=content.content_id).first()
            if not content:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Content not found"],
                )
            user.favourite_content.remove(content)
            session.commit()
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data={"Message": "unfavoured successfully"},
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )
