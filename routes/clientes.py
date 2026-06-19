from flask import Blueprint, request

from middleware.auth import jwt_required
from models.cliente import Cliente
from utils.responses import error, success
from utils.validators import require_fields

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


@clientes_bp.route("", methods=["GET"])
def list_clientes():
    """
    Lista clientes activos con paginación.
    ---
    tags:
      - Clientes
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
    responses:
      200:
        description: Listado paginado de clientes
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: array
              items:
                type: object
            meta:
              type: object
              properties:
                page:
                  type: integer
                per_page:
                  type: integer
                total:
                  type: integer
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    items, total = Cliente.list_paginated(page, per_page)
    return success(
        items,
        meta={"page": page, "per_page": per_page, "total": total},
    )


@clientes_bp.route("/<int:cliente_id>", methods=["GET"])
def get_cliente(cliente_id):
    """
    Obtiene el detalle de un cliente por su ID.
    ---
    tags:
      - Clientes
    parameters:
      - in: path
        name: cliente_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle del cliente
      404:
        description: Cliente no encontrado
    """
    cliente = Cliente.find_by_id(cliente_id)
    if not cliente:
        return error("Cliente no encontrado", 404)
    return success(cliente)


@clientes_bp.route("", methods=["POST"])
@jwt_required
def create_cliente():
    """
    Crea un nuevo cliente. Requiere JWT.
    ---
    tags:
      - Clientes
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
            - primer_nombre
            - apellido
            - dni
            - plan_id
          properties:
            usuario_id:
              type: integer
            primer_nombre:
              type: string
            segundo_nombre:
              type: string
            apellido:
              type: string
            segundo_apellido:
              type: string
            dni:
              type: string
            codigo_pais:
              type: string
            codigo_area:
              type: string
            numero_telefono:
              type: string
            plan_id:
              type: integer
            creditos:
              type: integer
              default: 0
    responses:
      201:
        description: Cliente creado
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
    """
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
    """
    Actualiza un cliente existente. Requiere JWT.
    ---
    tags:
      - Clientes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: cliente_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - primer_nombre
            - apellido
            - dni
            - plan_id
          properties:
            primer_nombre:
              type: string
            segundo_nombre:
              type: string
            apellido:
              type: string
            segundo_apellido:
              type: string
            dni:
              type: string
            codigo_pais:
              type: string
            codigo_area:
              type: string
            numero_telefono:
              type: string
            plan_id:
              type: integer
    responses:
      200:
        description: Cliente actualizado
      400:
        description: Faltan campos requeridos
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Cliente no encontrado
    """
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
    """
    Desactiva un cliente (soft delete vía estado de usuario). Requiere JWT.
    ---
    tags:
      - Clientes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: cliente_id
        type: integer
        required: true
    responses:
      200:
        description: Cliente desactivado
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Cliente no encontrado
    """
    if not Cliente.find_by_id(cliente_id):
        return error("Cliente no encontrado", 404)

    Cliente.deactivate(cliente_id)
    return success(message="Cliente desactivado")
