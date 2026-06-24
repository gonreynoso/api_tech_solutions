from utils.db import query


class Cliente:
    """Tabla: cliente(cliente_id, usuario_id, primer_nombre, segundo_nombre, apellido,
    segundo_apellido, dni, codigo_pais, codigo_area, numero_telefono, fecha_alta,
    creditos, plan_id, created_at, updated_at). El email y estado viven en usuario."""

    _SELECT = (
        "SELECT c.*, u.email, u.estado FROM cliente c "
        "JOIN usuario u ON u.usuario_id = c.usuario_id"
    )

    @staticmethod
    def list_paginated(page=1, per_page=20):
        offset = (page - 1) * per_page
        items = query(
            f"{Cliente._SELECT} WHERE u.estado = 'activo' "
            "ORDER BY c.cliente_id DESC LIMIT %s OFFSET %s",
            (per_page, offset),
        )
        total = query(
            "SELECT COUNT(*) AS count FROM cliente c "
            "JOIN usuario u ON u.usuario_id = c.usuario_id WHERE u.estado = 'activo'",
            fetch="one",
        )
        return items, total["count"]

    @staticmethod
    def find_by_id(cliente_id):
        return query(
            f"{Cliente._SELECT} WHERE c.cliente_id = %s", (cliente_id,), fetch="one"
        )

    @staticmethod
    def create(
        usuario_id,
        primer_nombre,
        apellido,
        dni,
        plan_id,
        segundo_nombre=None,
        segundo_apellido=None,
        codigo_pais=None,
        codigo_area=None,
        numero_telefono=None,
        creditos=0,
    ):
        return query(
            "INSERT INTO cliente (usuario_id, primer_nombre, segundo_nombre, apellido, "
            "segundo_apellido, dni, codigo_pais, codigo_area, numero_telefono, "
            "creditos, plan_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (
                usuario_id,
                primer_nombre,
                segundo_nombre,
                apellido,
                segundo_apellido,
                dni,
                codigo_pais,
                codigo_area,
                numero_telefono,
                creditos,
                plan_id,
            ),
            fetch="one",
        )

    @staticmethod
    def update(
        cliente_id,
        primer_nombre,
        apellido,
        dni,
        plan_id,
        segundo_nombre=None,
        segundo_apellido=None,
        codigo_pais=None,
        codigo_area=None,
        numero_telefono=None,
    ):
        return query(
            "UPDATE cliente SET primer_nombre = %s, segundo_nombre = %s, apellido = %s, "
            "segundo_apellido = %s, dni = %s, codigo_pais = %s, codigo_area = %s, "
            "numero_telefono = %s, plan_id = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE cliente_id = %s RETURNING *",
            (
                primer_nombre,
                segundo_nombre,
                apellido,
                segundo_apellido,
                dni,
                codigo_pais,
                codigo_area,
                numero_telefono,
                plan_id,
                cliente_id,
            ),
            fetch="one",
        )

    @staticmethod
    def deactivate(cliente_id):
        query(
            "UPDATE usuario SET estado = 'inactivo' WHERE usuario_id = "
            "(SELECT usuario_id FROM cliente WHERE cliente_id = %s)",
            (cliente_id,),
            fetch="none",
        )
