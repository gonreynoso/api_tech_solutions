"""Seed script for Consultora Tech Solutions API.

Usage:
    python seed.py            # insert sample data (idempotent, skips if already seeded)
    python seed.py --reset    # TRUNCATE all tables first, then insert fresh data
"""

import argparse

from werkzeug.security import generate_password_hash

from utils.db import query

DEFAULT_PASSWORD = "Password123"

PLANS = [
    ("Basico", 9999.00, 10, 72),
    ("Profesional", 24999.00, 30, 24),
    ("Premium", 49999.00, 100, 4),
]

SERVICIOS = [
    ("Auditoria Financiera", "Revisión integral de balances y flujos de caja.", "finanzas"),
    ("Campaña de Marketing Digital", "Gestión de campañas en redes y SEM.", "marketing"),
    ("Selección de Personal", "Búsqueda y selección de talento.", "recursos_humanos"),
    ("Desarrollo de Sitio Web", "Diseño y desarrollo de sitios a medida.", "desarrollo_web"),
    ("Optimización Logística", "Mejora de rutas y gestión de stock.", "logistica"),
    ("Implementación de Chatbot IA", "Chatbot con IA para atención al cliente.", "inteligencia_artificial"),
    ("Gestión de Proyectos PMO", "Acompañamiento PMO en proyectos clave.", "gestion_proyectos"),
    ("Compliance Normativo", "Revisión de cumplimiento legal y normativo.", "cumplimiento_legal"),
]

USUARIOS = [
    ("admin@techsolutions.com", "administrador", None),
    ("consultor@techsolutions.com", "consultor", None),
    ("cliente1@techsolutions.com", "cliente", "Basico"),
    ("cliente2@techsolutions.com", "cliente", "Premium"),
    ("cliente3@techsolutions.com", "cliente", "Profesional"),
    ("cliente4@techsolutions.com", "cliente", "Basico"),
    ("cliente5@techsolutions.com", "cliente", "Premium"),
    ("cliente6@techsolutions.com", "cliente", "Profesional"),
    ("cliente7@techsolutions.com", "cliente", "Basico"),
    ("cliente8@techsolutions.com", "cliente", "Premium"),
]

CLIENTES_DATA = {
    "cliente1@techsolutions.com": {
        "primer_nombre": "Lucia",
        "apellido": "Fernandez",
        "dni": "30111222",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "41234567",
        "creditos": 5,
    },
    "cliente2@techsolutions.com": {
        "primer_nombre": "Martin",
        "apellido": "Gomez",
        "dni": "30333444",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "47654321",
        "creditos": 50,
    },
    "cliente3@techsolutions.com": {
        "primer_nombre": "Carolina",
        "apellido": "Sosa",
        "dni": "31222111",
        "codigo_pais": "54",
        "codigo_area": "351",
        "numero_telefono": "5551234",
        "creditos": 20,
    },
    "cliente4@techsolutions.com": {
        "primer_nombre": "Diego",
        "apellido": "Acosta",
        "dni": "32333222",
        "codigo_pais": "54",
        "codigo_area": "261",
        "numero_telefono": "5552345",
        "creditos": 8,
    },
    "cliente5@techsolutions.com": {
        "primer_nombre": "Valentina",
        "apellido": "Romero",
        "dni": "33444333",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "5553456",
        "creditos": 80,
    },
    "cliente6@techsolutions.com": {
        "primer_nombre": "Nicolas",
        "apellido": "Paz",
        "dni": "34555444",
        "codigo_pais": "54",
        "codigo_area": "341",
        "numero_telefono": "5554567",
        "creditos": 25,
    },
    "cliente7@techsolutions.com": {
        "primer_nombre": "Florencia",
        "apellido": "Diaz",
        "dni": "35666555",
        "codigo_pais": "54",
        "codigo_area": "11",
        "numero_telefono": "5555678",
        "creditos": 3,
    },
    "cliente8@techsolutions.com": {
        "primer_nombre": "Ramiro",
        "apellido": "Suarez",
        "dni": "36777666",
        "codigo_pais": "54",
        "codigo_area": "221",
        "numero_telefono": "5556789",
        "creditos": 95,
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
    asignaciones = {
        "Basico": servicio_ids[:2],
        "Profesional": servicio_ids[:5],
        "Premium": servicio_ids,
    }
    count = 0
    for nombre_plan, servicios in asignaciones.items():
        for servicio_id in servicios:
            query(
                "INSERT INTO plan_servicio (plan_id, servicio_id) VALUES (%s, %s)",
                (plan_ids[nombre_plan], servicio_id),
                fetch="none",
            )
            count += 1
    print(f"Relaciones plan_servicio creadas: {count}")


def seed_usuarios_y_clientes(plan_ids):
    hashed = generate_password_hash(DEFAULT_PASSWORD)
    for email, rol, plan_nombre in USUARIOS:
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
    print(f"Usuarios creados: {[u[0] for u in USUARIOS]}")
    print(f"Password para todos los usuarios de prueba: {DEFAULT_PASSWORD}")


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
