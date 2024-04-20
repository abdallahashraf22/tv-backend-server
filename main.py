import uvicorn
import traceback
import logging.config

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from utils.log_utils import LOGGING_CONFIG
from utils.response import ReturnResponse

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("TV_backend")
app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            content=ReturnResponse.return_response(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                is_success=False,
                errors=[str(e)],
            ),
        )


app.middleware('http')(catch_exceptions_middleware)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)
