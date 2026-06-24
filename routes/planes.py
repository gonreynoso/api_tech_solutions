from flask import Blueprint, request

from middleware.auth import jwt_required
from models.plan import Plan
from utils.responses import error, success
from utils.validators import require_fields

planes_bp = Blueprint("planes", __name__, url_prefix="/api/planes")


@planes_bp.route("", methods=["GET"])
def list_planes():
    """
    Lista todos los planes disponibles.
    ---
    tags:
      - Planes
    responses:
      200:
        description: Listado de planes
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
    return success(Plan.list_all())


@planes_bp.route("/<int:plan_id>", methods=["GET"])
def get_plan(plan_id):
    """
    Obtiene el detalle de un plan por su ID.
    ---
    tags:
      - Planes
    parameters:
      - in: path
        name: plan_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle del plan
      404:
        description: Plan no encontrado
    """
    plan = Plan.find_by_id(plan_id)
    if not plan:
        return error("Plan no encontrado", 404)
    return success(plan)


@planes_bp.route("", methods=["POST"])
@jwt_required
def create_plan():
    """
    Crea un nuevo plan (CU-06 Gestionar clientes y planes). Requiere JWT.
    ---
    tags:
      - Planes
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre_plan
            - precio
            - creditos
            - tiempo_respuesta
          properties:
            nombre_plan:
              type: string
              enum: [Básico, Profesional, Premium]
            precio:
              type: number
            creditos:
              type: integer
            tiempo_respuesta:
              type: integer
    responses:
      201:
        description: Plan creado
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
    """
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["nombre_plan", "precio", "creditos", "tiempo_respuesta"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    plan = Plan.create(
        nombre_plan=data["nombre_plan"],
        precio=data["precio"],
        creditos=data["creditos"],
        tiempo_respuesta=data["tiempo_respuesta"],
    )
    return success(plan, message="Plan creado", status=201)


@planes_bp.route("/<int:plan_id>", methods=["PUT"])
@jwt_required
def update_plan(plan_id):
    """
    Actualiza un plan existente, incluyendo su baja (estado_plan). Requiere JWT.
    ---
    tags:
      - Planes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: plan_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre_plan
            - precio
            - creditos
            - tiempo_respuesta
            - estado_plan
          properties:
            nombre_plan:
              type: string
            precio:
              type: number
            creditos:
              type: integer
            tiempo_respuesta:
              type: integer
            estado_plan:
              type: string
              enum: [activo, discontinuado]
    responses:
      200:
        description: Plan actualizado
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Plan no encontrado
    """
    if not Plan.find_by_id(plan_id):
        return error("Plan no encontrado", 404)

    data = request.get_json(silent=True) or {}
    missing = require_fields(
        data, ["nombre_plan", "precio", "creditos", "tiempo_respuesta", "estado_plan"]
    )
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    plan = Plan.update(
        plan_id,
        nombre_plan=data["nombre_plan"],
        precio=data["precio"],
        creditos=data["creditos"],
        tiempo_respuesta=data["tiempo_respuesta"],
        estado_plan=data["estado_plan"],
    )
    return success(plan, message="Plan actualizado")
