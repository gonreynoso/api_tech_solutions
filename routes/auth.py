import datetime

import jwt
from flask import Blueprint, request
from werkzeug.security import check_password_hash

from config import Config
from models.usuario import Usuario
from utils.responses import error, success
from utils.validators import is_valid_email, require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _generate_tokens(user):
    now = datetime.datetime.utcnow()
    access_payload = {
        "user_id": user["usuario_id"],
        "email": user["email"],
        "rol": user["rol"],
        "exp": now + datetime.timedelta(hours=Config.JWT_ACCESS_EXPIRES_HOURS),
    }
    refresh_payload = {
        "user_id": user["usuario_id"],
        "type": "refresh",
        "exp": now + datetime.timedelta(days=Config.JWT_REFRESH_EXPIRES_DAYS),
    }
    access_token = jwt.encode(access_payload, Config.JWT_SECRET, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, Config.JWT_SECRET, algorithm="HS256")
    return access_token, refresh_token


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica un usuario y devuelve tokens JWT.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: usuario@email.com
            password:
              type: string
              example: secreto123
    responses:
      200:
        description: Login exitoso
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
                user:
                  type: object
                  properties:
                    usuario_id:
                      type: integer
                    email:
                      type: string
                    rol:
                      type: string
      400:
        description: Faltan campos requeridos o email inválido
      401:
        description: Credenciales inválidas
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["email", "password"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    email = data["email"]
    password = data["password"]

    if not is_valid_email(email):
        return error("Email inválido", 400)

    user = Usuario.find_by_email(email)
    if not user or not check_password_hash(user["contraseña"], password):
        return error("Credenciales inválidas", 401)

    access_token, _refresh_token = _generate_tokens(user)
    Usuario.update_token(user["usuario_id"], access_token)

    return success(
        {
            "access_token": access_token,
            "refresh_token": _refresh_token,
            "user": {
                "usuario_id": user["usuario_id"],
                "email": user["email"],
                "rol": user["rol"],
            },
        },
        message="Login exitoso",
    )


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Renueva el access token a partir de un refresh token válido.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refresh_token
          properties:
            refresh_token:
              type: string
    responses:
      200:
        description: Tokens renovados
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
      400:
        description: Falta refresh_token
      401:
        description: Refresh token inválido, expirado o de tipo incorrecto
      404:
        description: Usuario no encontrado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["refresh_token"])
    if missing:
        return error("Falta refresh_token", 400)

    try:
        payload = jwt.decode(
            data["refresh_token"], Config.JWT_SECRET, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        return error("Refresh token expirado", 401)
    except jwt.InvalidTokenError:
        return error("Refresh token inválido", 401)

    if payload.get("type") != "refresh":
        return error("Token no es de tipo refresh", 401)

    user = Usuario.find_by_id(payload["user_id"])
    if not user:
        return error("Usuario no encontrado", 404)

    access_token, refresh_token = _generate_tokens(user)
    Usuario.update_token(user["usuario_id"], access_token)

    return success({"access_token": access_token, "refresh_token": refresh_token})
