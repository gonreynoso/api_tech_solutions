from psycopg2.extras import Json

from utils.db import query


class IntegracionExterna:
    """Tabla: integracion_externa(integracion_id, sistema_externo, tipo_evento,
    registro_id, tabla_origen, estado, respuesta, intentos, ultimo_intento,
    fecha_creacion, created_at). sistema_externo: PagoNet|CRMMax|NotiSys|
    AnalytixPro|VeriCheck|WhatsApp. estado: pendiente|enviado|confirmado|error."""

    _SELECT = "SELECT * FROM integracion_externa"

    @staticmethod
    def create(sistema_externo, tipo_evento, registro_id, tabla_origen, estado, respuesta):
        return query(
            "INSERT INTO integracion_externa (sistema_externo, tipo_evento, "
            "registro_id, tabla_origen, estado, respuesta, intentos, "
            "ultimo_intento, fecha_creacion) "
            "VALUES (%s, %s, %s, %s, %s, %s, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) "
            "RETURNING *",
            (sistema_externo, tipo_evento, registro_id, tabla_origen, estado, Json(respuesta)),
            fetch="one",
        )

    @staticmethod
    def list_paginated(page=1, per_page=20, sistema_externo=None, estado=None):
        page = max(int(page), 1)
        per_page = min(max(int(per_page), 1), 100)
        offset = (page - 1) * per_page
        filters = []
        params = []
        if sistema_externo:
            filters.append("sistema_externo = %s")
            params.append(sistema_externo)
        if estado:
            filters.append("estado = %s")
            params.append(estado)
        where = f" WHERE {' AND '.join(filters)}" if filters else ""

        items = query(
            f"{IntegracionExterna._SELECT}{where} "
            "ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s",
            (*params, per_page, offset),
        )
        total = query(
            f"SELECT COUNT(*) AS count FROM integracion_externa{where}",
            tuple(params),
            fetch="one",
        )
        return items, total["count"]

    @staticmethod
    def find_by_id(integracion_id):
        return query(
            f"{IntegracionExterna._SELECT} WHERE integracion_id = %s",
            (integracion_id,),
            fetch="one",
        )
