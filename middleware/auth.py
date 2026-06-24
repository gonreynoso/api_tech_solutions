from functools import wraps

import jwt
from flask import g, request

from config import Config
from utils.responses import error


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return error("Token no provisto", 401)

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return error("Token expirado", 401)
        except jwt.InvalidTokenError:
            return error("Token inválido", 401)

        g.user_id = payload.get("user_id")
        g.user_email = payload.get("email")
        g.user_rol = payload.get("rol")
        return f(*args, **kwargs)

    return decorated
