from flask import Blueprint, request

from middleware.auth import jwt_required
from models.integracion_externa import IntegracionExterna
from utils.responses import error, success

integraciones_bp = Blueprint(
    "integraciones", __name__, url_prefix="/api/integraciones"
)

SISTEMAS_VALIDOS = {"PagoNet", "CRMMax", "NotiSys", "AnalytixPro", "VeriCheck", "WhatsApp"}
ESTADOS_VALIDOS = {"pendiente", "enviado", "confirmado", "error"}


@integraciones_bp.route("", methods=["GET"])
@jwt_required
def list_integraciones():
    """
    Lista el historial de integraciones con sistemas externos (HU15). Requiere JWT.
    ---
    tags:
      - Integraciones
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
        name: sistema_externo
        type: string
        enum: [PagoNet, CRMMax, NotiSys, AnalytixPro, VeriCheck, WhatsApp]
      - in: query
        name: estado
        type: string
        enum: [pendiente, enviado, confirmado, error]
    responses:
      200:
        description: Listado paginado de integraciones, más recientes primero
      400:
        description: Filtro inválido
      401:
        description: Token no provisto, inválido o expirado
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    sistema_externo = request.args.get("sistema_externo")
    estado = request.args.get("estado")

    if sistema_externo and sistema_externo not in SISTEMAS_VALIDOS:
        return error("sistema_externo inválido", 400)
    if estado and estado not in ESTADOS_VALIDOS:
        return error("estado inválido", 400)

    items, total = IntegracionExterna.list_paginated(
        page=page,
        per_page=per_page,
        sistema_externo=sistema_externo,
        estado=estado,
    )
    return success(items, meta={"page": page, "per_page": per_page, "total": total})


@integraciones_bp.route("/errores", methods=["GET"])
@jwt_required
def list_integraciones_errores():
    """
    Lista solo integraciones con estado 'error' (HU22). Requiere JWT.
    ---
    tags:
      - Integraciones
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
        name: sistema_externo
        type: string
        enum: [PagoNet, CRMMax, NotiSys, AnalytixPro, VeriCheck, WhatsApp]
    responses:
      200:
        description: Listado paginado de integraciones fallidas
      400:
        description: Filtro inválido
      401:
        description: Token no provisto, inválido o expirado
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    sistema_externo = request.args.get("sistema_externo")

    if sistema_externo and sistema_externo not in SISTEMAS_VALIDOS:
        return error("sistema_externo inválido", 400)

    items, total = IntegracionExterna.list_paginated(
        page=page,
        per_page=per_page,
        sistema_externo=sistema_externo,
        estado="error",
    )
    return success(items, meta={"page": page, "per_page": per_page, "total": total})


@integraciones_bp.route("/<int:integracion_id>", methods=["GET"])
@jwt_required
def get_integracion(integracion_id):
    """
    Obtiene el detalle de una integración por su ID. Requiere JWT.
    ---
    tags:
      - Integraciones
    security:
      - Bearer: []
    parameters:
      - in: path
        name: integracion_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle de la integración
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Integración no encontrada
    """
    integracion = IntegracionExterna.find_by_id(integracion_id)
    if not integracion:
        return error("Integración no encontrada", 404)
    return success(integracion)
