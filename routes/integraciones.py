from flask import Blueprint, request

from middleware.auth import jwt_required
from models.integracion_externa import IntegracionExterna
from utils.responses import error, success
from utils.validators import require_fields

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


@integraciones_bp.route("/simular", methods=["POST"])
@jwt_required
def simular_integracion():
    """
    Registra una integración simulada para la demo del Equipo 5. Requiere JWT.
    ---
    tags:
      - Integraciones
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - sistema_externo
            - tipo_evento
          properties:
            sistema_externo:
              type: string
              enum: [PagoNet, CRMMax, NotiSys, AnalytixPro, VeriCheck, WhatsApp]
            tipo_evento:
              type: string
            cliente_id:
              type: integer
            forzar_error:
              type: boolean
              default: false
    responses:
      201:
        description: Integración simulada registrada en el historial
      400:
        description: Faltan campos requeridos o sistema_externo inválido
      401:
        description: Token no provisto, inválido o expirado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["sistema_externo", "tipo_evento"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    if data["sistema_externo"] not in SISTEMAS_VALIDOS:
        return error("sistema_externo inválido", 400)

    forzar_error = bool(data.get("forzar_error", False))
    estado = "error" if forzar_error else "confirmado"
    respuesta = {
        "simulacion": True,
        "mensaje": (
            f"Error simulado al comunicarse con {data['sistema_externo']}."
            if forzar_error
            else f"Comunicación simulada con {data['sistema_externo']} realizada correctamente."
        ),
    }

    integracion = IntegracionExterna.create(
        sistema_externo=data["sistema_externo"],
        tipo_evento=data["tipo_evento"],
        registro_id=data.get("cliente_id"),
        tabla_origen="simulacion",
        estado=estado,
        respuesta=respuesta,
    )
    return success(integracion, message="Integración simulada", status=201)
