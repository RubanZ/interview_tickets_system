from typing import Annotated

from pydantic import BaseModel, Field, EmailStr

from app.models import TicketStatuses


class PaginationRequest(BaseModel):
    page_size: Annotated[int, Field(ge=1, le=100, default=10)]
    page: Annotated[int, Field(ge=1, default=1)]


class TicketsListQuery(PaginationRequest):
    pass


class TicketCreateBody(BaseModel):
    subject: Annotated[str, Field(max_length=256)]
    text: Annotated[str, Field(max_length=2048)]
    email: EmailStr


class TicketUpdateBody(BaseModel):
    status: TicketStatuses
