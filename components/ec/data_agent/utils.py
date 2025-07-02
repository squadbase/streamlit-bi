from typing import Any, Optional, Self

from pydantic import BaseModel


class ExtendedBaseModel(BaseModel):
    @classmethod
    def safe_model_validate_json(cls, json_str: str) -> Optional[Self]:
        try:
            return super().model_validate_json(json_str)
        except Exception:
            return None

    @classmethod
    def safe_model_validate(cls, obj: Any) -> Optional[Self]:
        try:
            return super().model_validate(obj)
        except Exception:
            return None
