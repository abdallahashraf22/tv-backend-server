from http import HTTPStatus
from typing import Annotated

import sqlalchemy.exc
from pydantic import BaseModel, constr, Field
from fastapi import APIRouter, Response

from models import engine, Genre
from sqlalchemy.orm import Session
from utils.response import ReturnResponse

genres_router = APIRouter(prefix="/genres", tags=["genres"])


@genres_router.get("/")
def get_genres(response: Response):
    try:
        with Session(engine) as session:
            genres = session.query(Genre).all()
            response.status_code = HTTPStatus.OK.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data=genres
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"]
        )


class GenreBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]


@genres_router.post("/")
def create_genre(genre: GenreBase, response: Response):
    try:
        with Session(engine) as session:
            new_genre = Genre(name=genre.name)
            session.add(new_genre)
            session.commit()
            response.status_code = HTTPStatus.CREATED.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.CREATED.value,
                is_success=True,
                data={"id": new_genre.id, "name": new_genre.name}
            )
    except sqlalchemy.exc.IntegrityError as e:
        response.status_code = HTTPStatus.BAD_REQUEST.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:Probably a duplicate genre"]
        )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"]
        )


@genres_router.put("/{genre_id}")
def edit_genre(genre_id: int, genre: GenreBase, response: Response):
    try:
        with Session(engine) as session:
            genre_to_update = session.get(Genre, genre_id)
            if genre_to_update:
                genre_to_update.name = genre.name
                session.commit()
                response.status_code = HTTPStatus.OK.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.OK.value,
                    is_success=True,
                    data={"id": genre_to_update.id, "name": genre.name}
                )
            else:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Genre not found"]
                )
    except sqlalchemy.exc.IntegrityError as e:
        response.status_code = HTTPStatus.BAD_REQUEST.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.BAD_REQUEST.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:Probably a duplicate genre"]
        )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"]
        )


@genres_router.delete("/{genre_id}")
def delete_genre(genre_id: int, response: Response):
    try:
        with Session(engine) as session:
            genre = session.get(Genre, genre_id)
            if genre:
                session.delete(genre)
                session.commit()
                response.status_code = HTTPStatus.OK.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.OK.value,
                    is_success=True,
                    data={"message": "Deleted genre successfully"}
                )
            else:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Genre not found"]
                )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"]
        )
