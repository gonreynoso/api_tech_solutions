from flask import Blueprint, request

from middleware.auth import jwt_required
from models.servicio import Servicio
from utils.responses import error, success
from utils.validators import require_fields

servicios_bp = Blueprint("servicios", __name__, url_prefix="/api/servicios")


@servicios_bp.route("", methods=["GET"])
def list_servicios():
    """
    Lista servicios, con filtros opcionales por área y estado.
    ---
    tags:
      - Servicios
    parameters:
      - in: query
        name: area
        type: string
        enum: [finanzas, marketing, recursos_humanos, desarrollo_web, logistica, inteligencia_artificial, gestion_proyectos, cumplimiento_legal]
      - in: query
        name: estado
        type: string
    responses:
      200:
        description: Listado de servicios
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: array
              items:
                type: object
    """
    area = request.args.get("area")
    estado = request.args.get("estado")
    items = Servicio.list_filtered(area=area, estado=estado)
    return success(items)


@servicios_bp.route("/<int:servicio_id>", methods=["GET"])
def get_servicio(servicio_id):
    """
    Obtiene el detalle de un servicio por su ID.
    ---
    tags:
      - Servicios
    parameters:
      - in: path
        name: servicio_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle del servicio
      404:
        description: Servicio no encontrado
    """
    servicio = Servicio.find_by_id(servicio_id)
    if not servicio:
        return error("Servicio no encontrado", 404)
    return success(servicio)


@servicios_bp.route("/by-plan/<int:plan_id>", methods=["GET"])
def get_servicios_by_plan(plan_id):
    """
    Lista los servicios incluidos en un plan dado.
    ---
    tags:
      - Servicios
    parameters:
      - in: path
        name: plan_id
        type: integer
        required: true
    responses:
      200:
        description: Servicios asociados al plan
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: array
              items:
                type: object
    """
    items = Servicio.find_by_plan(plan_id)
    return success(items)


@servicios_bp.route("", methods=["POST"])
@jwt_required
def create_servicio():
    """
    Crea un nuevo servicio. Requiere JWT.
    ---
    tags:
      - Servicios
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre_servicio
            - descripcion
            - area
          properties:
            nombre_servicio:
              type: string
            descripcion:
              type: string
            area:
              type: string
              enum: [finanzas, marketing, recursos_humanos, desarrollo_web, logistica, inteligencia_artificial, gestion_proyectos, cumplimiento_legal]
            estado_servicio:
              type: string
              default: activo
    responses:
      201:
        description: Servicio creado
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["nombre_servicio", "descripcion", "area"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    servicio = Servicio.create(
        data["nombre_servicio"],
        data["descripcion"],
        data["area"],
        data.get("estado_servicio", "activo"),
    )
    return success(servicio, message="Servicio creado", status=201)


@servicios_bp.route("/<int:servicio_id>", methods=["PUT"])
@jwt_required
def update_servicio(servicio_id):
    """
    Actualiza un servicio existente. Requiere JWT.
    ---
    tags:
      - Servicios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: servicio_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre_servicio
            - descripcion
            - area
            - estado_servicio
          properties:
            nombre_servicio:
              type: string
            descripcion:
              type: string
            area:
              type: string
              enum: [finanzas, marketing, recursos_humanos, desarrollo_web, logistica, inteligencia_artificial, gestion_proyectos, cumplimiento_legal]
            estado_servicio:
              type: string
    responses:
      200:
        description: Servicio actualizado
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Servicio no encontrado
    """
    if not Servicio.find_by_id(servicio_id):
        return error("Servicio no encontrado", 404)

    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["nombre_servicio", "descripcion", "area", "estado_servicio"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    servicio = Servicio.update(
        servicio_id,
        data["nombre_servicio"],
        data["descripcion"],
        data["area"],
        data["estado_servicio"],
    )
    return success(servicio, message="Servicio actualizado")
