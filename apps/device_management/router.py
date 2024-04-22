from http import HTTPStatus
from typing import Annotated

import sqlalchemy
from pydantic import BaseModel, Field
from fastapi import APIRouter, Response, Depends
from pydantic_extra_types.mac_address import MacAddress

from auth import FullUser, is_user
from utils.response import ReturnResponse
from models import engine, User, Device, Session

device_router = APIRouter(prefix="/devices", tags=["device"])


class DeviceData(BaseModel):
    mac_address: MacAddress
    language: Annotated[str, Field(min_length=2, max_length=3, default="en")]
    timezone: Annotated[str, Field(min_length=2, max_length=6, default="UTC")]


@device_router.get("/")
def get_devices(
    response: Response, current_user: Annotated[FullUser, Depends(is_user)]
):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(id=current_user.id).first()
            devices = user.devices
            response.status_code = HTTPStatus.OK.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value, is_success=True, data=devices
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@device_router.post("/")
def attach_device_to_user(
    response: Response,
    device_data: DeviceData,
    current_user: Annotated[FullUser, Depends(is_user)],
):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(id=current_user.id).first()
            device = Device(**device_data.dict())
            user.devices.append(device)
            session.commit()
            response.status_code = HTTPStatus.CREATED.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.CREATED.value,
                is_success=True,
                data={
                    "mac_address": device.mac_address,
                    "language": device.language,
                    "timezone": device.timezone,
                },
            )
    except sqlalchemy.exc.IntegrityError as e:
        response.status_code = HTTPStatus.BAD_REQUEST.value
        return ReturnResponse.return_response(
            is_success=False,
            status_code=HTTPStatus.BAD_REQUEST.value,
            errors=[f"{e.__class__.__name__}: Probably a duplicate mac address"],
        )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )


@device_router.delete("/{device_id}")
def delete_device(
    response: Response,
    device_id: int,
    current_user: Annotated[FullUser, Depends(is_user)],
):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(id=current_user.id).first()
            device = session.query(Device).filter_by(id=device_id).first()
            if not device:
                response.status_code = HTTPStatus.NOT_FOUND.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.NOT_FOUND.value,
                    is_success=False,
                    errors=["Device not found"],
                )
            if device.user_id != user.id:
                response.status_code = HTTPStatus.FORBIDDEN.value
                return ReturnResponse.return_response(
                    status_code=HTTPStatus.FORBIDDEN.value,
                    is_success=False,
                    errors=["You can't delete another user's device"],
                )
            user.devices.remove(device)
            session.commit()
            response.status_code = HTTPStatus.OK.value
            return ReturnResponse.return_response(
                status_code=HTTPStatus.OK.value,
                is_success=True,
                data={"device_id": device.id},
            )
    except Exception as e:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return ReturnResponse.return_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            is_success=False,
            errors=[f"{e.__class__.__name__}:{str(e)}"],
        )
