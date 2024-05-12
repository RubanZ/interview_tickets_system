from flask import Blueprint, request, Response
from app.cache import cache
from app.crud.comment import TicketCommentCRUD
from app.crud.ticket import TicketCRUD
from app.schemas.requests.comments import TicketCommentCreateBody
from app.schemas.requests.tickets import (
    TicketsListQuery,
    TicketCreateBody,
    TicketUpdateBody,
)
from app.schemas.responses.ticket import (
    TicketPaginationResponse,
    TicketResponse,
    TicketCommentResponse,
)

ticket_blueprint = Blueprint("tickets", __name__)


@ticket_blueprint.route("/", methods=["GET"])
@cache.cached(timeout=15, key_prefix="tickets-list", query_string=True)
def get_tickets():
    query = TicketsListQuery(**request.args.to_dict())
    total, db_result = TicketCRUD.get_tickets(query.page, query.page_size)
    return Response(
        TicketPaginationResponse(
            total=total,
            items=[TicketResponse.model_validate(ticket) for ticket in db_result],
        ).model_dump_json(),
        200,
        mimetype="application/json",
    )


@ticket_blueprint.route("/", methods=["POST"])
def create_ticket():
    body = TicketCreateBody(**request.json)

    new_ticket = TicketCRUD.create_ticket(body.subject, body.text, body.email)

    cache.clear()
    return Response(
        TicketResponse.model_validate(new_ticket).model_dump_json(),
        201,
        mimetype="application/json",
    )


@ticket_blueprint.route("/<int:ticket_id>/", methods=["GET"])
@cache.cached(timeout=30, key_prefix="ticket")
def get_ticket(ticket_id: int):
    ticket = TicketCRUD.get_ticket(ticket_id)

    return Response(
        TicketResponse.model_validate(ticket).model_dump_json(),
        200,
        mimetype="application/json",
    )


@ticket_blueprint.route("/<int:ticket_id>/", methods=["PUT"])
def update_ticket(ticket_id: int):
    body = TicketUpdateBody(**request.json)

    updated_ticket = TicketCRUD.update_ticket(ticket_id, body.status)

    cache.clear()
    return Response(
        TicketResponse.model_validate(updated_ticket).model_dump_json(),
        200,
        mimetype="application/json",
    )


@ticket_blueprint.route("/<int:ticket_id>/comments/", methods=["POST"])
def add_comment(ticket_id: int):
    body = TicketCommentCreateBody(**request.json)

    new_comment = TicketCommentCRUD.create_ticket_comment(
        ticket_id, body.text, body.email
    )

    cache.clear()
    return Response(
        TicketCommentResponse.model_validate(new_comment).model_dump_json(),
        201,
        mimetype="application/json",
    )
