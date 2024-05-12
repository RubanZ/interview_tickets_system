from pydantic import BaseModel


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int
    items: list[BaseResponse]


class ErrorResponse(BaseModel):
    message: str
    details: dict[str, str] | None = None

    class Config:
        json_schema_extra = {
            "example": {"message": "Validation error", "details": {"field": "value"}}
        }
