"""Cliente mock de PagoNet.

PagoNet es la plataforma externa de facturación y pagos descrita en el caso.
Esta función simula el envío del cargo y devuelve una respuesta con la misma
forma que tendría la integración real.
"""

import uuid


def enviar_facturacion(cliente_id, nombre_cliente, plan_nuevo, monto, servicio="Asesoría"):
    return {
        "pagonet_id": f"pago_{uuid.uuid4().hex[:12]}",
        "status": "accepted",
        "cliente_id": cliente_id,
        "nombre_cliente": nombre_cliente,
        "plan_nuevo": plan_nuevo,
        "monto_a_facturar": monto,
        "servicio": servicio,
    }
