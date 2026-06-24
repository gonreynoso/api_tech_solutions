from utils.db import query


class Notificacion:
    """Tabla: notificacion(notificacion_id, usuario_id, tipo, asunto, contenido,
    leida, fecha_creacion, fecha_lectura, created_at)."""

    _SELECT = "SELECT * FROM notificacion"

    @staticmethod
    def list_paginated(usuario_id, page=1, per_page=20, leida=None):
        offset = (page - 1) * per_page
        filters = ["usuario_id = %s"]
        params = [usuario_id]
        if leida is not None:
            filters.append("leida = %s")
            params.append(leida)
        where = f" WHERE {' AND '.join(filters)}"

        items = query(
            f"{Notificacion._SELECT}{where} ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s",
            (*params, per_page, offset),
        )
        total = query(
            f"SELECT COUNT(*) AS count FROM notificacion{where}",
            tuple(params),
            fetch="one",
        )
        return items, total["count"]

    @staticmethod
    def find_by_id(notificacion_id):
        return query(
            f"{Notificacion._SELECT} WHERE notificacion_id = %s",
            (notificacion_id,),
            fetch="one",
        )

    @staticmethod
    def create(usuario_id, tipo, asunto, contenido):
        return query(
            "INSERT INTO notificacion (usuario_id, tipo, asunto, contenido, leida, "
            "fecha_creacion) VALUES (%s, %s, %s, %s, false, CURRENT_TIMESTAMP) "
            "RETURNING *",
            (usuario_id, tipo, asunto, contenido),
            fetch="one",
        )

    @staticmethod
    def mark_as_read(notificacion_id):
        return query(
            "UPDATE notificacion SET leida = true, fecha_lectura = CURRENT_TIMESTAMP "
            "WHERE notificacion_id = %s RETURNING *",
            (notificacion_id,),
            fetch="one",
        )
