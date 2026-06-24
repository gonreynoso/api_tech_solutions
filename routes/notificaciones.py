from flask import Blueprint, request

from middleware.auth import jwt_required
from models.notificacion import Notificacion
from utils.responses import error, success
from utils.validators import require_fields

notificaciones_bp = Blueprint(
    "notificaciones", __name__, url_prefix="/api/notificaciones"
)


@notificaciones_bp.route("", methods=["GET"])
@jwt_required
def list_notificaciones():
    """
    Lista notificaciones de un usuario (CU-05 Consultar notificaciones). Requiere JWT.
    ---
    tags:
      - Notificaciones
    security:
      - Bearer: []
    parameters:
      - in: query
        name: usuario_id
        type: integer
        required: true
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
      - in: query
        name: leida
        type: boolean
    responses:
      200:
        description: Listado paginado de notificaciones, más recientes primero
      400:
        description: Falta usuario_id
      401:
        description: Token no provisto, inválido o expirado
    """
    usuario_id = request.args.get("usuario_id", type=int)
    if usuario_id is None:
        return error("Falta el parámetro usuario_id", 400)

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    leida_raw = request.args.get("leida")
    leida = None if leida_raw is None else leida_raw.lower() == "true"

    items, total = Notificacion.list_paginated(usuario_id, page, per_page, leida)
    return success(items, meta={"page": page, "per_page": per_page, "total": total})


@notificaciones_bp.route("", methods=["POST"])
@jwt_required
def create_notificacion():
    """
    Crea una notificación para un usuario. Requiere JWT.
    ---
    tags:
      - Notificaciones
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - usuario_id
            - tipo
            - asunto
            - contenido
          properties:
            usuario_id:
              type: integer
            tipo:
              type: string
            asunto:
              type: string
            contenido:
              type: string
    responses:
      201:
        description: Notificación creada
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["usuario_id", "tipo", "asunto", "contenido"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    notificacion = Notificacion.create(
        usuario_id=data["usuario_id"],
        tipo=data["tipo"],
        asunto=data["asunto"],
        contenido=data["contenido"],
    )
    return success(notificacion, message="Notificación creada", status=201)


@notificaciones_bp.route("/<int:notificacion_id>/leida", methods=["PUT"])
@jwt_required
def mark_notificacion_leida(notificacion_id):
    """
    Marca una notificación como leída (CU-05). Requiere JWT.
    ---
    tags:
      - Notificaciones
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notificacion_id
        type: integer
        required: true
    responses:
      200:
        description: Notificación marcada como leída
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Notificación no encontrada
    """
    if not Notificacion.find_by_id(notificacion_id):
        return error("Notificación no encontrada", 404)

    notificacion = Notificacion.mark_as_read(notificacion_id)
    return success(notificacion, message="Notificación marcada como leída")
