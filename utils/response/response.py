from abc import ABC
from typing import Dict
from fastapi.encoders import jsonable_encoder


class ReturnResponse(ABC):
    @classmethod
    def return_response(
        cls, status_code, is_success=None, data=None, errors=None
    ) -> Dict:
        if is_success:
            return jsonable_encoder(
                {"statusCode": status_code, "data": data, "is_success": True}
            )
        else:
            return jsonable_encoder(
                {"statusCode": status_code, "errors": errors, "is_success": False}
            )
