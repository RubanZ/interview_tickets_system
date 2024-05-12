from typing import Annotated

from pydantic import BaseModel, Field, EmailStr


class TicketCommentCreateBody(BaseModel):
    text: Annotated[str, Field(max_length=2048)]
    email: EmailStr
