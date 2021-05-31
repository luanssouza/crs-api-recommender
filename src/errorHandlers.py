from werkzeug.exceptions import HTTPException
from flask import Blueprint
import logging

error_blueprint = Blueprint('error_handlers', __name__)

@error_blueprint.app_errorhandler(Exception)
def handle_exception(e):
    logging.error(e)
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return { "message" : "Internal Server Error!", "status": 500 }, 500
