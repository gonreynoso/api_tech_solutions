"""Cliente mock de CRMMax.

CRMMax no tiene una API real disponible para este TP: esta función simula
la sincronización bidireccional descrita en el DER (acontecimiento 9) y
devuelve una respuesta con la misma forma que tendría una integración real,
para que el llamador la persista en integracion_externa sin distinguir
implementación real de mock.
"""

import uuid


def sync_cliente(cliente):
    return {
        "crmmax_contact_id": f"crm_{uuid.uuid4().hex[:12]}",
        "status": "synced",
        "cliente_id": cliente["cliente_id"],
    }
