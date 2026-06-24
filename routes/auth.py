import datetime

import jwt
from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from models.cliente import Cliente
from models.integracion_externa import IntegracionExterna
from models.usuario import Usuario
from utils import vericheck
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


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registra un nuevo cliente, validando su identidad con VeriCheck (CU-01).
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
            - primer_nombre
            - apellido
            - dni
            - plan_id
          properties:
            email:
              type: string
            password:
              type: string
            primer_nombre:
              type: string
            segundo_nombre:
              type: string
            apellido:
              type: string
            segundo_apellido:
              type: string
            dni:
              type: string
            codigo_pais:
              type: string
            codigo_area:
              type: string
            numero_telefono:
              type: string
            plan_id:
              type: integer
    responses:
      201:
        description: Cliente registrado, autenticado y con identidad validada
      400:
        description: Faltan campos requeridos o email inválido
      401:
        description: VeriCheck rechazó la validación de identidad
      409:
        description: Ya existe una cuenta con ese email
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(
        data, ["email", "password", "primer_nombre", "apellido", "dni", "plan_id"]
    )
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    email = data["email"]
    if not is_valid_email(email):
        return error("Email inválido", 400)

    if Usuario.find_by_email(email):
        return error("Ya existe una cuenta asociada a ese email", 409)

    nombre_completo = f"{data['primer_nombre']} {data['apellido']}"
    resultado_vericheck = vericheck.validate_identity(data["dni"], nombre_completo)
    IntegracionExterna.create(
        sistema_externo="VeriCheck",
        tipo_evento="validacion_identidad",
        registro_id=None,
        tabla_origen="usuario",
        estado="confirmado" if resultado_vericheck["resultado"] == "aprobada" else "error",
        respuesta=resultado_vericheck,
    )

    if resultado_vericheck["resultado"] != "aprobada":
        return error(
            "No se pudo validar la identidad",
            401,
            {"motivo": resultado_vericheck.get("motivo")},
        )

    contraseña_hash = generate_password_hash(data["password"])
    usuario = Usuario.create(email, contraseña_hash, rol="cliente")

    cliente = Cliente.create(
        usuario_id=usuario["usuario_id"],
        primer_nombre=data["primer_nombre"],
        apellido=data["apellido"],
        dni=data["dni"],
        plan_id=data["plan_id"],
        segundo_nombre=data.get("segundo_nombre"),
        segundo_apellido=data.get("segundo_apellido"),
        codigo_pais=data.get("codigo_pais"),
        codigo_area=data.get("codigo_area"),
        numero_telefono=data.get("numero_telefono"),
    )

    access_token, refresh_token = _generate_tokens(usuario)
    Usuario.update_token(usuario["usuario_id"], access_token)

    return success(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario": {
                "usuario_id": usuario["usuario_id"],
                "email": usuario["email"],
                "rol": usuario["rol"],
            },
            "cliente": cliente,
        },
        message="Cliente registrado",
        status=201,
    )


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
