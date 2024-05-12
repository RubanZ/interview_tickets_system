from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestException
from app.models import db, TicketComment, Ticket
from app.models import TicketStatuses


class TicketCommentCRUD:
    @staticmethod
    def create_ticket_comment(ticket_id: int, text: str, email: str) -> TicketComment:
        """
        Создание комментария к тикету
        :param ticket_id: ID Тикета к которому добавляется комментарий
        :param text: Текст комментария
        :param email: Автор комментария
        :return: Объект комментария
        """

        with Session(db.engine) as session:
            ticket = (
                session.query(Ticket)
                .options(joinedload(Ticket.comments))
                .get(ticket_id)
            )
            if ticket.status == TicketStatuses.closed:
                raise BadRequestException("Ticket is closed")

            comment = TicketComment(ticket_id=ticket.id, text=text, email=email)
            session.add(comment)
            session.commit()
            session.refresh(comment)

        return comment
