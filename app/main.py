from flask import Flask, Response
from flask_migrate import Migrate
from pydantic import ValidationError

from app.cache import cache
from app.core.config import settings
from app.core.exceptions import BadRequestException
from app.models import db
from app.routes import ticket_blueprint
from app.schemas.responses.base import ErrorResponse

app = Flask(__name__)
app.config.update({
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SQLALCHEMY_DATABASE_URI": settings.DATABASE_URL,
    "TESTING": settings.TESTING,
    "CACHE_TYPE": "redis" if settings.TESTING is False else "SimpleCache",
    "CACHE_REDIS_URL": settings.REDIS_URL,
})
db.init_app(app)
migrate = Migrate(app, db)
cache.init_app(app)

app.register_blueprint(ticket_blueprint, url_prefix="/tickets")


@app.errorhandler(ValidationError)
def handle_bad_request(e: ValidationError):
    """Возвращаем первую ошибку валидации в виде ответа с кодом 400"""
    error = e.errors()[0]
    return Response(
        ErrorResponse(
            message="Validation error", details={error["loc"][0]: error["msg"]}
        ).json(),
        400,
        mimetype="application/json",
    )


@app.errorhandler(BadRequestException)
def handle_bad_request_basic(e: BadRequestException):
    return Response(
        ErrorResponse(message=e.message).json(), 400, mimetype="application/json"
    )


@app.errorhandler(404)
def handle_not_found(e):
    return Response(
        ErrorResponse(message=e.description).json(), 404, mimetype="application/json"
    )


if __name__ == "__main__":
    app.run()
