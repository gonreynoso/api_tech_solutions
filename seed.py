"""Seed script for Consultora Tech Solutions API.

Datos oficiales según el caso de Consultora Tech Solutions (servicios, planes
y relaciones plan_servicio documentados en el caso de la cátedra).

Usage:
    python seed.py            # insert sample data (idempotent, skips if already seeded)
    python seed.py --reset    # TRUNCATE all tables first, then insert fresh data
"""

import argparse

from werkzeug.security import generate_password_hash

from utils.db import query

PLANS = [
    ("Basico", 99.99, 30, 48),
    ("Profesional", 299.99, 100, 24),
    ("Premium", 499.99, 300, 4),
]

SERVICIOS = [
    ("Consultor en Finanzas y Contabilidad", "Asesoría en gestión financiera y tributaria", "finanzas"),
    ("Consultor en Marketing Digital", "Estrategias de publicidad y posicionamiento en redes sociales", "marketing"),
    ("Consultor en Recursos Humanos y Talento", "Selección y capacitación de personal", "recursos_humanos"),
    ("Consultor en Desarrollo Web y UX/UI", "Diseño y optimización de plataformas digitales", "desarrollo_web"),
    ("Consultor en Logística y Cadena de Suministro", "Gestión de inventario y distribución", "logistica"),
    ("Consultor en Inteligencia Artificial y Machine Learning", "Soluciones de IA para automatizar procesos", "inteligencia_artificial"),
    ("Consultor en Gestión de Proyectos Agile", "Capacitación y soporte en metodologías ágiles", "gestion_proyectos"),
    ("Consultor en Cumplimiento Legal y Normativo", "Asesoría en normativas legales por sector", "cumplimiento_legal"),
]

# Índices sobre SERVICIOS (0 = Finanzas ... 7 = Legal), según el caso oficial:
# Básico: Finanzas, Marketing, Desarrollo Web. Profesional: todos menos Legal. Premium: todos.
PLAN_SERVICIO_INDICES = {
    "Basico": [0, 1, 3],
    "Profesional": [0, 1, 2, 3, 4, 5, 6],
    "Premium": [0, 1, 2, 3, 4, 5, 6, 7],
}

# (email, password, rol, plan_nombre o None si no es cliente)
USUARIOS = [
    ("admin@example.com", "admin123", "administrador", None),
    ("consultor@example.com", "consultor123", "consultor", None),
    ("cliente@example.com", "cliente123", "cliente", "Basico"),
    ("franco@example.com", "cliente123", "cliente", "Profesional"),
    ("solange@example.com", "cliente123", "cliente", "Premium"),
]

CLIENTES_DATA = {
    "cliente@example.com": {
        "primer_nombre": "Cliente",
        "apellido": "Demo",
        "dni": "30100100",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "41234567",
        "creditos": 25,
    },
    "franco@example.com": {
        "primer_nombre": "Franco",
        "apellido": "Asistente",
        "dni": "30200200",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "42345678",
        "creditos": 50,
    },
    "solange@example.com": {
        "primer_nombre": "Solange",
        "apellido": "Asistente",
        "dni": "30300300",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "43456789",
        "creditos": 100,
    },
}

TABLES_IN_FK_ORDER = ["plan_servicio", "cliente", "servicio", "plan", "usuario"]


def reset_tables():
    for table in TABLES_IN_FK_ORDER:
        query(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE", fetch="none")
    print("Tablas truncadas.")


def already_seeded():
    row = query("SELECT COUNT(*) AS count FROM usuario", fetch="one")
    return row["count"] > 0


def seed_plans():
    plan_ids = {}
    for nombre_plan, precio, creditos, tiempo_respuesta in PLANS:
        row = query(
            "INSERT INTO plan (nombre_plan, precio, creditos, tiempo_respuesta) "
            "VALUES (%s, %s, %s, %s) RETURNING plan_id",
            (nombre_plan, precio, creditos, tiempo_respuesta),
            fetch="one",
        )
        plan_ids[nombre_plan] = row["plan_id"]
    print(f"Planes creados: {list(plan_ids.keys())}")
    return plan_ids


def seed_servicios():
    servicio_ids = []
    for nombre_servicio, descripcion, area in SERVICIOS:
        row = query(
            "INSERT INTO servicio (nombre_servicio, descripcion, area) "
            "VALUES (%s, %s, %s) RETURNING servicio_id",
            (nombre_servicio, descripcion, area),
            fetch="one",
        )
        servicio_ids.append(row["servicio_id"])
    print(f"Servicios creados: {len(servicio_ids)}")
    return servicio_ids


def seed_plan_servicio(plan_ids, servicio_ids):
    count = 0
    for nombre_plan, indices in PLAN_SERVICIO_INDICES.items():
        for i in indices:
            query(
                "INSERT INTO plan_servicio (plan_id, servicio_id) VALUES (%s, %s)",
                (plan_ids[nombre_plan], servicio_ids[i]),
                fetch="none",
            )
            count += 1
    print(f"Relaciones plan_servicio creadas: {count}")


def seed_usuarios_y_clientes(plan_ids):
    for email, password, rol, plan_nombre in USUARIOS:
        hashed = generate_password_hash(password)
        usuario = query(
            "INSERT INTO usuario (email, contraseña, rol, estado) "
            "VALUES (%s, %s, %s, 'activo') RETURNING usuario_id",
            (email, hashed, rol),
            fetch="one",
        )
        if rol == "cliente":
            datos = CLIENTES_DATA[email]
            query(
                "INSERT INTO cliente (usuario_id, primer_nombre, apellido, dni, "
                "codigo_pais, codigo_area, numero_telefono, creditos, plan_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    usuario["usuario_id"],
                    datos["primer_nombre"],
                    datos["apellido"],
                    datos["dni"],
                    datos["codigo_pais"],
                    datos["codigo_area"],
                    datos["numero_telefono"],
                    datos["creditos"],
                    plan_ids[plan_nombre],
                ),
                fetch="none",
            )
    print("Usuarios creados:")
    for email, password, rol, _ in USUARIOS:
        print(f"  {email} / {password} ({rol})")


def main():
    parser = argparse.ArgumentParser(description="Seed de datos de prueba")
    parser.add_argument(
        "--reset", action="store_true", help="Trunca todas las tablas antes de insertar"
    )
    args = parser.parse_args()

    if args.reset:
        reset_tables()
    elif already_seeded():
        print("Las tablas ya tienen datos. Usá --reset para reiniciar y volver a sembrar.")
        return

    plan_ids = seed_plans()
    servicio_ids = seed_servicios()
    seed_plan_servicio(plan_ids, servicio_ids)
    seed_usuarios_y_clientes(plan_ids)
    print("Seed completado.")


if __name__ == "__main__":
    main()
