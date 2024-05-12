from app.core.exceptions import BadRequestException
from app.models import db, TicketComment, Ticket
from app.models import TicketStatuses


class TicketCommentCRUD:
    @staticmethod
    def create_ticket_comment(ticket: Ticket, text: str, email: str) -> TicketComment:
        """
        Создание комментария к тикету
        :param ticket: Тикет к которому добавляется комментарий
        :param text: Текст комментария
        :param email: Автор комментария
        :return: Объект комментария
        """
        if ticket.status == TicketStatuses.closed:
            raise BadRequestException("Ticket is closed")

        comment = TicketComment(ticket_id=ticket.id, text=text, email=email)
        db.session.add(comment)
        db.session.commit()
        return comment
