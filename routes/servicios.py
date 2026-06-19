from flask import Blueprint, request

from middleware.auth import jwt_required
from models.servicio import Servicio
from utils.responses import error, success
from utils.validators import require_fields

servicios_bp = Blueprint("servicios", __name__, url_prefix="/api/servicios")


@servicios_bp.route("", methods=["GET"])
def list_servicios():
    area = request.args.get("area")
    estado = request.args.get("estado")
    items = Servicio.list_filtered(area=area, estado=estado)
    return success(items)


@servicios_bp.route("/<int:servicio_id>", methods=["GET"])
def get_servicio(servicio_id):
    servicio = Servicio.find_by_id(servicio_id)
    if not servicio:
        return error("Servicio no encontrado", 404)
    return success(servicio)


@servicios_bp.route("/by-plan/<int:plan_id>", methods=["GET"])
def get_servicios_by_plan(plan_id):
    items = Servicio.find_by_plan(plan_id)
    return success(items)


@servicios_bp.route("", methods=["POST"])
@jwt_required
def create_servicio():
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
