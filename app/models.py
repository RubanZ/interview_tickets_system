import enum
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, Text, Integer, Enum, func, TIMESTAMP, event, ForeignKey


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class TicketStatuses(str, enum.Enum):
    open = "open"
    waiting_for_answer = "waiting_for_answer"
    answered = "answered"
    closed = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(256), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    status: Mapped[TicketStatuses] = mapped_column(
        Enum(TicketStatuses), default=TicketStatuses.open, nullable=False, index=True
    )
    created_at: Mapped[int] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[int] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    comments: Mapped[List["TicketComment"]] = relationship(
        "TicketComment", back_populates="ticket", lazy="subquery"
    )

    def __repr__(self):
        return "<Ticket id={} subject={}>".format(self.id, self.subject)


class TicketComment(Base):
    __tablename__ = "tickets_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tickets.id", ondelete="CASCADE"), index=True
    )
    ticket = relationship("Ticket", back_populates="comments")
    created_at: Mapped[int] = mapped_column(TIMESTAMP, server_default=func.now())
    email: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)


# На всякий случай, приводим email к нижнему регистру перед сохранением
def before_insert_listener(mapper, connection, target):
    target.email = target.email.lower()


# Привязываем функцию-обработчик к событию before_insert
event.listen(Ticket, "before_insert", before_insert_listener)
event.listen(TicketComment, "before_insert", before_insert_listener)
