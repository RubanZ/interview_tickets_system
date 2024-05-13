from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestException
from app.models import Ticket, db
from app.models import TicketStatuses


class TicketCRUD:
    @staticmethod
    def get_ticket(ticket_id: int) -> Ticket:
        """
        Получение тикета по идентификатору
        :param ticket_id: id тикета
        :return: объект тикета
        """
        with Session(db.engine) as session:
            ticket = (
                session.query(Ticket)
                .options(joinedload(Ticket.comments))
                .get(ticket_id)
            )
            return ticket

    @staticmethod
    def get_tickets(page: int, per_page: int) -> (int, list[Ticket]):
        """
        Получение списка тикетов
        :param page: текущая страница
        :param per_page: количество элементов на странице
        :return: кортеж из общего количества тикетов и списка тикетов
        """
        with Session(db.engine) as session:
            total = session.query(Ticket).count()

            sort_logic = case(
                {"open": 1, "waiting_for_answer": 0, "answered": 2, "closed": 3},
                value=Ticket.status,
            ).label("status")

            page_items = (
                session.query(Ticket)
                .options(joinedload(Ticket.comments))
                .order_by(sort_logic, Ticket.created_at.asc())
                .limit(per_page)
                .offset((page - 1) * per_page)
            )
            return total, page_items

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

        with Session(db.engine) as session:
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
        return ticket

    @staticmethod
    def update_ticket(ticket_id: int, new_status: TicketStatuses) -> Ticket:
        """
        Обновление статуса тикета. Тикет создается в статусе “открыт”, может перейти в “отвечен” или “закрыт”, из
        отвечен в “ожидает ответа” или “закрыт”, статус “закрыт” финальный (нельзя изменить статус или добавить комментарий)
        :param ticket_id: id тикета
        :param new_status: новый статус тикета
        :return: Объект тикета
        """

        def is_allowed(status) -> bool:
            """
            Проверка возможности изменения статуса тикета
            :return: True если изменение статуса возможно, иначе False
            """
            if status == TicketStatuses.open:
                return new_status in [TicketStatuses.answered, TicketStatuses.closed]

            if ticket.status == TicketStatuses.answered:
                return new_status in [
                    TicketStatuses.waiting_for_answer,
                    TicketStatuses.closed,
                ]

            if ticket.status == TicketStatuses.waiting_for_answer:
                return new_status in [TicketStatuses.answered, TicketStatuses.closed]

        with Session(db.engine) as session:
            ticket = (
                session.query(Ticket)
                .options(joinedload(Ticket.comments))
                .with_for_update()
                .get(ticket_id)
            )
            if not is_allowed(ticket.status):
                raise BadRequestException(
                    "Action is not allowed for current ticket status"
                )
            ticket.status = new_status
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
        return ticket
