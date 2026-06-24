from flask import Blueprint, request

from middleware.auth import jwt_required
from models.caso import Caso
from utils.responses import error, success
from utils.validators import require_fields

casos_bp = Blueprint("casos", __name__, url_prefix="/api/casos")

ESTADOS_VALIDOS = {"asignado", "en_atención", "en_progreso", "resuelto", "escalado"}


@casos_bp.route("", methods=["GET"])
@jwt_required
def list_casos():
    """
    Lista casos con paginación. Filtra por consultor o estado (CU-09). Requiere JWT.
    ---
    tags:
      - Casos
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
        name: consultor_id
        type: integer
      - in: query
        name: estado_caso
        type: string
    responses:
      200:
        description: Listado paginado de casos
      401:
        description: Token no provisto, inválido o expirado
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    consultor_id = request.args.get("consultor_id", type=int)
    estado_caso = request.args.get("estado_caso")

    items, total = Caso.list_paginated(page, per_page, consultor_id, estado_caso)
    return success(items, meta={"page": page, "per_page": per_page, "total": total})


@casos_bp.route("/<int:caso_id>", methods=["GET"])
@jwt_required
def get_caso(caso_id):
    """
    Obtiene el detalle de un caso con datos del cliente (CU-10). Requiere JWT.
    ---
    tags:
      - Casos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: caso_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle del caso con datos del cliente asociado
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Caso no encontrado
    """
    caso = Caso.find_by_id(caso_id)
    if not caso:
        return error("Caso no encontrado", 404)
    return success(caso)


@casos_bp.route("", methods=["POST"])
@jwt_required
def create_caso():
    """
    Asigna un caso a un consultor (CU-08). Requiere JWT.
    ---
    tags:
      - Casos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - solicitud_id
            - cliente_id
            - consultor_id
          properties:
            solicitud_id:
              type: integer
            cliente_id:
              type: integer
            consultor_id:
              type: integer
    responses:
      201:
        description: Caso asignado con estado 'asignado'
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["solicitud_id", "cliente_id", "consultor_id"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    caso = Caso.create(
        solicitud_id=data["solicitud_id"],
        cliente_id=data["cliente_id"],
        consultor_id=data["consultor_id"],
    )
    return success(caso, message="Caso asignado", status=201)


@casos_bp.route("/<int:caso_id>", methods=["PUT"])
@jwt_required
def update_caso(caso_id):
    """
    Actualiza el estado, horas trabajadas y notas de un caso (CU-11). Requiere JWT.
    ---
    tags:
      - Casos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: caso_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - estado_caso
          properties:
            estado_caso:
              type: string
              enum: [asignado, en_atención, en_progreso, resuelto, escalado]
            horas_trabajadas:
              type: number
            notas_internas:
              type: string
    responses:
      200:
        description: Caso actualizado
      400:
        description: Falta el campo o el estado no es válido
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Caso no encontrado
    """
    if not Caso.find_by_id(caso_id):
        return error("Caso no encontrado", 404)

    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["estado_caso"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    if data["estado_caso"] not in ESTADOS_VALIDOS:
        return error("Estado no válido", 400, {"valid_states": sorted(ESTADOS_VALIDOS)})

    caso = Caso.update_estado(
        caso_id,
        estado_caso=data["estado_caso"],
        horas_trabajadas=data.get("horas_trabajadas"),
        notas_internas=data.get("notas_internas"),
    )
    return success(caso, message="Caso actualizado")
