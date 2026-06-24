"""Cliente mock de VeriCheck.

VeriCheck no tiene una API real disponible para este TP: esta función simula
la validación de identidad descrita en el DER (acontecimientos 13 y 14) y
devuelve una respuesta con la misma forma que tendría una integración real.
Rechaza únicamente DNIs vacíos o con formato inválido (no numérico); cualquier
otro caso se aprueba, ya que no hay un padrón real contra el cual validar.
"""


def validate_identity(dni, nombre):
    if not dni or not str(dni).strip().isdigit():
        return {"resultado": "rechazada", "motivo": "DNI con formato inválido"}
    return {"resultado": "aprobada", "dni": dni, "nombre": nombre}
