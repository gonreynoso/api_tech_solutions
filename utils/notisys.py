"""Cliente mock de NotiSys.

NotiSys es la plataforma de notificaciones multicanal (email + SMS) descrita
en el caso. Esta función simula el envío y devuelve una respuesta con la
misma forma que tendría la integración real.
"""

import uuid


def enviar_notificacion(tipo, cliente_id, mensaje):
    return {
        "notisys_id": f"noti_{uuid.uuid4().hex[:12]}",
        "status": "delivered",
        "tipo": tipo,
        "cliente_id": cliente_id,
        "mensaje": mensaje,
    }
