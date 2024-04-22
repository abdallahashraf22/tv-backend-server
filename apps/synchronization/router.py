import json
import logging
from typing import Annotated, Optional

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError
from fastapi import APIRouter, WebSocket, Depends, Request, HTTPException

from auth import is_user, FullUser
from models import User, Content, engine, Session, UserWatchingContent

sync_router = APIRouter(prefix="/sync")
logger = logging.getLogger(f"TV_backend.{__name__}")
templates = Jinja2Templates(directory="templates")


class SyncData(BaseModel):
    content_id: int
    timestamp: Annotated[Optional[str], Field(pattern="^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")] = None


@sync_router.get("/", response_class=HTMLResponse)
def sync_page(request: Request):
    return templates.TemplateResponse(name="watching.html", request=request)


@sync_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        await websocket.accept()
        user = is_user(token=token)
        user_id = user.__dict__.get("id")
        while True:
            data = await websocket.receive_text()
            sync_data = SyncData(**json.loads(data))
            print(sync_data)
            with Session(engine) as session:
                user = session.get(User, user_id)
                content = session.get(Content, sync_data.content_id)
                if content is None:
                    await websocket.send_text("Content not found")
                    await websocket.close()
                    break
                user_content_watching_row = session.query(UserWatchingContent).filter_by(user_id=user.id,
                                                                                         content_id=sync_data.content_id).first()
                if user_content_watching_row:
                    if sync_data.timestamp:
                        user_content_watching_row.timestamp = sync_data.timestamp
                        session.commit()
                        await websocket.send_text(sync_data.timestamp)
                    else:
                        await websocket.send_text(user_content_watching_row.timestamp)
                    continue
                else:
                    user_watching_content = UserWatchingContent(user_id=user.id, content_id=content.id,
                                                                timestamp="00:00:00")
                    session.add(user_watching_content)
                    session.commit()
                    await websocket.send_text("00:00:00")
                continue
    except ValidationError as e:
        logger.error(f"Error in validating json: {e.__class__.__name__}:{e}")
        await websocket.close()
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error in decoding json: {e.__class__.__name__}:{e}")
        await websocket.close()
        return
    except HTTPException as e:
        logger.error(f"Error in validating user: {e.__class__.__name__}:{e}")
        await websocket.send_text("Invalid token")
        await websocket.close()
        return
    except Exception as e:
        logger.error(f"Error in websocket: {e.__class__.__name__}:{e}")
        await websocket.close()
        return
