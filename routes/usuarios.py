from middleware.auth import jwt_required
from flask import Blueprint

from models.usuario import Usuario
from utils.responses import error, success

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@usuarios_bp.route("", methods=["GET"])
@jwt_required
def list_usuarios():
    """
    Lista todos los usuarios (sin contraseña ni token). Requiere JWT.
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Listado de usuarios
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: array
              items:
                type: object
      401:
        description: Token no provisto, inválido o expirado
    """
    return success(Usuario.list_all())


@usuarios_bp.route("/<int:usuario_id>", methods=["GET"])
@jwt_required
def get_usuario(usuario_id):
    """
    Obtiene el detalle público de un usuario por su ID. Requiere JWT.
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: usuario_id
        type: integer
        required: true
    responses:
      200:
        description: Detalle del usuario
      401:
        description: Token no provisto, inválido o expirado
      404:
        description: Usuario no encontrado
    """
    usuario = Usuario.find_public_by_id(usuario_id)
    if not usuario:
        return error("Usuario no encontrado", 404)
    return success(usuario)
