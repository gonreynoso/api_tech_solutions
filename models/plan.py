from utils.db import query


class Plan:
    """Tabla: plan(plan_id, nombre_plan, precio, creditos, tiempo_respuesta,
    estado_plan, created_at, updated_at)"""

    @staticmethod
    def list_all():
        return query("SELECT * FROM plan ORDER BY plan_id")

    @staticmethod
    def find_by_id(plan_id):
        return query("SELECT * FROM plan WHERE plan_id = %s", (plan_id,), fetch="one")
