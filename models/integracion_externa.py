from psycopg2.extras import Json

from utils.db import query


class IntegracionExterna:
    """Tabla: integracion_externa(integracion_id, sistema_externo, tipo_evento,
    registro_id, tabla_origen, estado, respuesta, intentos, ultimo_intento,
    fecha_creacion, created_at). sistema_externo: PagoNet|CRMMax|NotiSys|
    AnalytixPro|VeriCheck|WhatsApp. estado: pendiente|enviado|confirmado|error."""

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
