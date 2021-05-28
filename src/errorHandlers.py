from werkzeug.exceptions import HTTPException
import logging

from __main__ import app

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(e)
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return { "message" : "Internal Server Error!", "status": 500 }, 500
