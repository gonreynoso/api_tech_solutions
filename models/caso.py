from utils.db import query


class Caso:
    """Tabla: caso(caso_id, solicitud_id, cliente_id, consultor_id, estado_caso,
    horas_trabajadas, notas_internas, fecha_asignacion, fecha_resolucion,
    created_at, updated_at)."""

    _SELECT = "SELECT * FROM caso"
    _SELECT_DETAIL = (
        "SELECT ca.*, c.primer_nombre, c.apellido, c.dni "
        "FROM caso ca JOIN cliente c ON c.cliente_id = ca.cliente_id"
    )

    @staticmethod
    def list_paginated(page=1, per_page=20, consultor_id=None, estado_caso=None):
        offset = (page - 1) * per_page
        filters = []
        params = []
        if consultor_id is not None:
            filters.append("consultor_id = %s")
            params.append(consultor_id)
        if estado_caso is not None:
            filters.append("estado_caso = %s")
            params.append(estado_caso)
        where = f" WHERE {' AND '.join(filters)}" if filters else ""

        items = query(
            f"{Caso._SELECT}{where} ORDER BY caso_id DESC LIMIT %s OFFSET %s",
            (*params, per_page, offset),
        )
        total = query(
            f"SELECT COUNT(*) AS count FROM caso{where}",
            tuple(params),
            fetch="one",
        )
        return items, total["count"]

    @staticmethod
    def find_by_id(caso_id):
        return query(
            f"{Caso._SELECT_DETAIL} WHERE ca.caso_id = %s", (caso_id,), fetch="one"
        )

    @staticmethod
    def create(solicitud_id, cliente_id, consultor_id):
        return query(
            "INSERT INTO caso (solicitud_id, cliente_id, consultor_id, estado_caso, "
            "fecha_asignacion) VALUES (%s, %s, %s, 'asignado', CURRENT_TIMESTAMP) "
            "RETURNING *",
            (solicitud_id, cliente_id, consultor_id),
            fetch="one",
        )

    @staticmethod
    def update_estado(caso_id, estado_caso, horas_trabajadas=None, notas_internas=None):
        fecha_resolucion_sql = (
            "CURRENT_TIMESTAMP" if estado_caso == "resuelto" else "fecha_resolucion"
        )
        return query(
            f"UPDATE caso SET estado_caso = %s, horas_trabajadas = COALESCE(%s, horas_trabajadas), "
            f"notas_internas = COALESCE(%s, notas_internas), "
            f"fecha_resolucion = {fecha_resolucion_sql}, updated_at = CURRENT_TIMESTAMP "
            "WHERE caso_id = %s RETURNING *",
            (estado_caso, horas_trabajadas, notas_internas, caso_id),
            fetch="one",
        )
