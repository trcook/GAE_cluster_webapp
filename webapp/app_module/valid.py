# key was to import flask and flask session
from flask import session
import flask
from functools import wraps
def validator(func):
    @wraps(func)
    def validator_in(*args, **kwargs):
        if session.get('validated',0)==0:
            return flask.abort(403)
        return func(*args, **kwargs)
    return validator_in
