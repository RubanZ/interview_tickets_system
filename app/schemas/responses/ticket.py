from datetime import datetime
from typing import Annotated

from pydantic import Field, EmailStr

from app.models import TicketStatuses

from app.schemas.responses.base import PaginationResponse, BaseResponse


class TicketCommentResponse(BaseResponse):
    id: int
    ticket_id: int
    text: str
    email: EmailStr
    created_at: datetime


class TicketResponse(BaseResponse):
    id: int
    subject: Annotated[str, Field(max_length=256)] = ""
    text: str = ""
    email: EmailStr
    status: TicketStatuses
    created_at: datetime
    updated_at: datetime
    comments: list[TicketCommentResponse] = []


class TicketPaginationResponse(PaginationResponse):
    items: list[TicketResponse] = []
