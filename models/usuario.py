from utils.db import query


class Usuario:
    """Tabla: usuario(usuario_id, email, contraseña, rol, estado, ultimo_acceso,
    token_jwt, created_at, updated_at)"""

    @staticmethod
    def find_by_email(email):
        return query(
            "SELECT * FROM usuario WHERE email = %s AND estado = 'activo'",
            (email,),
            fetch="one",
        )

    @staticmethod
    def find_by_id(usuario_id):
        return query(
            "SELECT * FROM usuario WHERE usuario_id = %s", (usuario_id,), fetch="one"
        )

    @staticmethod
    def list_all():
        return query(
            "SELECT usuario_id, email, rol, estado, ultimo_acceso, created_at "
            "FROM usuario ORDER BY usuario_id"
        )

    @staticmethod
    def find_public_by_id(usuario_id):
        return query(
            "SELECT usuario_id, email, rol, estado, ultimo_acceso, created_at "
            "FROM usuario WHERE usuario_id = %s",
            (usuario_id,),
            fetch="one",
        )

    @staticmethod
    def update_token(usuario_id, token_jwt):
        query(
            "UPDATE usuario SET token_jwt = %s, ultimo_acceso = CURRENT_TIMESTAMP "
            "WHERE usuario_id = %s",
            (token_jwt, usuario_id),
            fetch="none",
        )
