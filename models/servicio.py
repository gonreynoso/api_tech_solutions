from utils.db import query


class Servicio:
    """Tabla: servicio(servicio_id, nombre_servicio, descripcion, area, estado_servicio,
    created_at, updated_at). Relación con plan via plan_servicio(plan_id, servicio_id)."""

    @staticmethod
    def list_filtered(area=None, estado=None):
        sql = "SELECT * FROM servicio WHERE 1=1"
        params = []
        if area:
            sql += " AND area = %s"
            params.append(area)
        if estado:
            sql += " AND estado_servicio = %s"
            params.append(estado)
        sql += " ORDER BY servicio_id DESC"
        return query(sql, tuple(params))

    @staticmethod
    def find_by_id(servicio_id):
        return query(
            "SELECT * FROM servicio WHERE servicio_id = %s", (servicio_id,), fetch="one"
        )

    @staticmethod
    def find_by_plan(plan_id):
        return query(
            "SELECT s.* FROM servicio s "
            "JOIN plan_servicio ps ON ps.servicio_id = s.servicio_id "
            "WHERE ps.plan_id = %s",
            (plan_id,),
        )

    @staticmethod
    def create(nombre_servicio, descripcion, area, estado_servicio="activo"):
        return query(
            "INSERT INTO servicio (nombre_servicio, descripcion, area, estado_servicio) "
            "VALUES (%s, %s, %s, %s) RETURNING *",
            (nombre_servicio, descripcion, area, estado_servicio),
            fetch="one",
        )

    @staticmethod
    def update(servicio_id, nombre_servicio, descripcion, area, estado_servicio):
        return query(
            "UPDATE servicio SET nombre_servicio = %s, descripcion = %s, area = %s, "
            "estado_servicio = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE servicio_id = %s RETURNING *",
            (nombre_servicio, descripcion, area, estado_servicio, servicio_id),
            fetch="one",
        )
