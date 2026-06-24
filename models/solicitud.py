from utils.db import query


class Solicitud:
    """Tabla: solicitud(solicitud_id, cliente_id, servicio_id, fecha_creacion,
    estado_solicitud, prioridad, descripcion, created_at, updated_at)."""

    _SELECT = "SELECT * FROM solicitud"

    @staticmethod
    def list_paginated(page=1, per_page=20, cliente_id=None, estado_solicitud=None):
        offset = (page - 1) * per_page
        filters = []
        params = []
        if cliente_id is not None:
            filters.append("cliente_id = %s")
            params.append(cliente_id)
        if estado_solicitud is not None:
            filters.append("estado_solicitud = %s")
            params.append(estado_solicitud)
        where = f" WHERE {' AND '.join(filters)}" if filters else ""

        items = query(
            f"{Solicitud._SELECT}{where} ORDER BY solicitud_id DESC LIMIT %s OFFSET %s",
            (*params, per_page, offset),
        )
        total = query(
            f"SELECT COUNT(*) AS count FROM solicitud{where}",
            tuple(params),
            fetch="one",
        )
        return items, total["count"]

    @staticmethod
    def find_by_id(solicitud_id):
        return query(
            f"{Solicitud._SELECT} WHERE solicitud_id = %s", (solicitud_id,), fetch="one"
        )

    @staticmethod
    def create(cliente_id, servicio_id, descripcion, prioridad="media"):
        return query(
            "INSERT INTO solicitud (cliente_id, servicio_id, descripcion, prioridad, "
            "estado_solicitud) VALUES (%s, %s, %s, %s, 'pendiente') RETURNING *",
            (cliente_id, servicio_id, descripcion, prioridad),
            fetch="one",
        )

    @staticmethod
    def update_estado(solicitud_id, estado_solicitud):
        return query(
            "UPDATE solicitud SET estado_solicitud = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE solicitud_id = %s RETURNING *",
            (estado_solicitud, solicitud_id),
            fetch="one",
        )
