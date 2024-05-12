from sqlalchemy import case

from app.core.exceptions import BadRequestException
from app.models import Ticket, db
from app.models import TicketStatuses


class TicketCRUD:
    @staticmethod
    def get_ticket(ticket_id: int, for_update: bool = False) -> Ticket:
        """
        Получение тикета по идентификатору
        :param ticket_id: id тикета
        :param for_update: флаг, указывающий на необходимость тип запроса
        :return: объект тикета
        """
        ticket = db.session.query(Ticket).get(ticket_id)

        if for_update is True and ticket.status == TicketStatuses.closed:
            raise BadRequestException("Ticket is closed")

        return ticket

    @staticmethod
    def get_tickets(page: int, per_page: int) -> (int, list[Ticket]):
        """
        Получение списка тикетов
        :param page: текущая страница
        :param per_page: количество элементов на странице
        :return: кортеж из общего количества тикетов и списка тикетов
        """
        total = db.session.query(Ticket).count()

        sort_logic = case(
            {"open": 0, "waiting_for_answer": 1, "answered": 2, "closed": 3},
            value=Ticket.status,
        ).label("status")

        db_result = (
            db.session.query(Ticket)
            .order_by(sort_logic, Ticket.created_at.asc())
            .paginate(page=page, per_page=per_page)
        )
        return total, db_result

    @staticmethod
    def create_ticket(subject: str, text: str, email: str) -> Ticket:
        """
        Создание тикета
        :param subject: Тема тикета
        :param text: Текст тикета
        :param email: Email автора тикета
        :return: Объект тикета
        """
        ticket = Ticket(subject=subject, text=text, email=email)
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def update_ticket(ticket: Ticket, status: TicketStatuses) -> Ticket:
        """
        Обновление статуса тикета. Тикет создается в статусе “открыт”, может перейти в “отвечен” или “закрыт”, из
        отвечен в “ожидает ответа” или “закрыт”, статус “закрыт” финальный (нельзя изменить статус или добавить комментарий)
        :param ticket:
        :param status:
        :return:
        """

        def is_allowed() -> bool:
            """
            Проверка возможности изменения статуса тикета
            :return:
            """
            if ticket.status == TicketStatuses.open:
                return status in [TicketStatuses.answered, TicketStatuses.closed]

            if ticket.status == TicketStatuses.answered:
                return status in [
                    TicketStatuses.waiting_for_answer,
                    TicketStatuses.closed,
                ]

            if ticket.status == TicketStatuses.waiting_for_answer:
                return status in [TicketStatuses.answered, TicketStatuses.closed]

        if not is_allowed():
            raise BadRequestException("Action is not allowed for current ticket status")

        ticket.status = status
        db.session.commit()
        return ticket
