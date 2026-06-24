from flask import Blueprint, request

from middleware.auth import jwt_required
from models.solicitud import Solicitud
from utils.responses import error, success
from utils.validators import require_fields

solicitudes_bp = Blueprint("solicitudes", __name__, url_prefix="/api/solicitudes")

ESTADOS_VALIDOS = {"pendiente", "en_revisión", "aprobada", "rechazada", "resuelta"}


@solicitudes_bp.route("", methods=["GET"])
@jwt_required
def list_solicitudes():
    """
    Lista solicitudes con paginación. Filtra por cliente o estado. Requiere JWT.
    ---
    tags:
      - Solicitudes
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
      - in: query
        name: cliente_id
        type: integer
      - in: query
        name: estado_solicitud
        type: string
    responses:
      200:
        description: Listado paginado de solicitudes
      401:
        description: Token no provisto, inválido o expirado
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    cliente_id = request.args.get("cliente_id", type=int)
    estado_solicitud = request.args.get("estado_solicitud")

    items, total = Solicitud.list_paginated(page, per_page, cliente_id, estado_solicitud)
    return success(items, meta={"page": page, "per_page": per_page, "total": total})


@solicitudes_bp.route("/<int:solicitud_id>", methods=["GET"])
@jwt_required
def get_solicitud(solicitud_id):
    """
    Obtiene el detalle de una solicitud. Requiere JWT.
    ---
    tags:
      - Solicitudes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: solicitud_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle de la solicitud
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Solicitud no encontrada
    """
    solicitud = Solicitud.find_by_id(solicitud_id)
    if not solicitud:
        return error("Solicitud no encontrada", 404)
    return success(solicitud)


@solicitudes_bp.route("", methods=["POST"])
@jwt_required
def create_solicitud():
    """
    Crea una solicitud (CU-03 Realizar solicitud). Requiere JWT.
    ---
    tags:
      - Solicitudes
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - cliente_id
            - servicio_id
            - descripcion
          properties:
            cliente_id:
              type: integer
            servicio_id:
              type: integer
            descripcion:
              type: string
            prioridad:
              type: string
              enum: [baja, media, alta]
              default: media
    responses:
      201:
        description: Solicitud creada con estado 'pendiente'
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["cliente_id", "servicio_id", "descripcion"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    solicitud = Solicitud.create(
        cliente_id=data["cliente_id"],
        servicio_id=data["servicio_id"],
        descripcion=data["descripcion"],
        prioridad=data.get("prioridad", "media"),
    )
    return success(solicitud, message="Solicitud creada", status=201)


@solicitudes_bp.route("/<int:solicitud_id>/estado", methods=["PUT"])
@jwt_required
def update_estado_solicitud(solicitud_id):
    """
    Aprueba, rechaza o responde una solicitud (CU-07, CU-12). Requiere JWT.
    ---
    tags:
      - Solicitudes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: solicitud_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - estado_solicitud
          properties:
            estado_solicitud:
              type: string
              enum: [pendiente, en_revisión, aprobada, rechazada, resuelta]
    responses:
      200:
        description: Solicitud actualizada
      400:
        description: Falta el campo o el estado no es válido
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Solicitud no encontrada
    """
    if not Solicitud.find_by_id(solicitud_id):
        return error("Solicitud no encontrada", 404)

    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["estado_solicitud"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    if data["estado_solicitud"] not in ESTADOS_VALIDOS:
        return error("Estado no válido", 400, {"valid_states": sorted(ESTADOS_VALIDOS)})

    solicitud = Solicitud.update_estado(solicitud_id, data["estado_solicitud"])
    return success(solicitud, message="Solicitud actualizada")
