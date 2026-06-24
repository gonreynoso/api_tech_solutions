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

    @staticmethod
    def create(nombre_plan, precio, creditos, tiempo_respuesta):
        return query(
            "INSERT INTO plan (nombre_plan, precio, creditos, tiempo_respuesta, "
            "estado_plan) VALUES (%s, %s, %s, %s, 'activo') RETURNING *",
            (nombre_plan, precio, creditos, tiempo_respuesta),
            fetch="one",
        )

    @staticmethod
    def update(plan_id, nombre_plan, precio, creditos, tiempo_respuesta, estado_plan):
        return query(
            "UPDATE plan SET nombre_plan = %s, precio = %s, creditos = %s, "
            "tiempo_respuesta = %s, estado_plan = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE plan_id = %s RETURNING *",
            (nombre_plan, precio, creditos, tiempo_respuesta, estado_plan, plan_id),
            fetch="one",
        )
