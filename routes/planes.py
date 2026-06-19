from flask import Blueprint

from models.plan import Plan
from utils.responses import error, success

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
