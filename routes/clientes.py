from flask import Blueprint, request

from middleware.auth import jwt_required
from models.cliente import Cliente
from utils.responses import error, success
from utils.validators import require_fields

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


@clientes_bp.route("", methods=["GET"])
def list_clientes():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    items, total = Cliente.list_paginated(page, per_page)
    return success(
        items,
        meta={"page": page, "per_page": per_page, "total": total},
    )


@clientes_bp.route("/<int:cliente_id>", methods=["GET"])
def get_cliente(cliente_id):
    cliente = Cliente.find_by_id(cliente_id)
    if not cliente:
        return error("Cliente no encontrado", 404)
    return success(cliente)


@clientes_bp.route("", methods=["POST"])
@jwt_required
def create_cliente():
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["usuario_id", "primer_nombre", "apellido", "dni", "plan_id"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    cliente = Cliente.create(
        usuario_id=data["usuario_id"],
        primer_nombre=data["primer_nombre"],
        apellido=data["apellido"],
        dni=data["dni"],
        plan_id=data["plan_id"],
        segundo_nombre=data.get("segundo_nombre"),
        segundo_apellido=data.get("segundo_apellido"),
        codigo_pais=data.get("codigo_pais"),
        codigo_area=data.get("codigo_area"),
        numero_telefono=data.get("numero_telefono"),
        creditos=data.get("creditos", 0),
    )
    return success(cliente, message="Cliente creado", status=201)


@clientes_bp.route("/<int:cliente_id>", methods=["PUT"])
@jwt_required
def update_cliente(cliente_id):
    if not Cliente.find_by_id(cliente_id):
        return error("Cliente no encontrado", 404)

    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["primer_nombre", "apellido", "dni", "plan_id"])
    if missing:
        return error("Faltan campos requeridos", 400, {"missing": missing})

    cliente = Cliente.update(
        cliente_id,
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
    return success(cliente, message="Cliente actualizado")


@clientes_bp.route("/<int:cliente_id>", methods=["DELETE"])
@jwt_required
def deactivate_cliente(cliente_id):
    if not Cliente.find_by_id(cliente_id):
        return error("Cliente no encontrado", 404)

    Cliente.deactivate(cliente_id)
    return success(message="Cliente desactivado")
