# Módulo de Integraciones Externas — Equipo 5

Este documento describe lo que el **Equipo 5** agregó al repo: integraciones con 6 sistemas externos (CRMMax, VeriCheck, NotiSys, PagoNet, AnalytixPro, WhatsApp), endpoints de auditoría y triggers automáticos que disparan al ocurrir ciertos eventos.

> Para consumir la API base (clientes, planes, etc.) ver [`CONSUMIR_API.md`](./CONSUMIR_API.md). Acá solo está lo que sumó Equipo 5.

---

## 1. Side effects en endpoints existentes (importante)

Equipo 5 **no rompió** ningún endpoint, pero sí agregó comportamiento automático en algunos. Si tu equipo consume estos endpoints, leé esto:

### `PUT /api/clientes/<id>` — actualizar cliente

Ahora, además del update, dispara automáticamente:

| Trigger | Sistema | Cuándo |
|---|---|---|
| Cambio de `dni` o `plan_id` | **VeriCheck** | Antes del update; si rechaza → **bloquea con 403** |
| Siempre, después del update | **CRMMax** | Sincroniza el perfil actualizado |
| Cambio de `plan_id` | **PagoNet** | Facturación con retry (2 intentos) |
| Cambio de `plan_id` | **NotiSys** | Notifica al cliente del cambio aprobado |

Si un sistema externo falla (excepto VeriCheck rechazo), el update **no se bloquea** — el error queda registrado en `integracion_externa` (estado `error`).

### `POST /api/solicitudes` — crear solicitud

Tras crear, dispara **NotiSys** con `tipo_evento="solicitud_creada"`.

### `PUT /api/solicitudes/<id>/estado` — cambiar estado de solicitud

Tras el cambio, dispara **NotiSys** con `tipo_evento="cambio_estado_solicitud"`.

---

## 2. Endpoints nuevos

Todos requieren JWT (mismo flow que el resto del API, ver `CONSUMIR_API.md` sección 3).

| Método | Ruta | Para qué | HU |
|---|---|---|---|
| `GET` | `/api/integraciones` | Historial paginado con filtros `sistema_externo`, `estado` | HU15 |
| `GET` | `/api/integraciones/errores` | Solo registros con `estado="error"` | HU22 |
| `GET` | `/api/integraciones/<id>` | Detalle de una integración | — |
| `POST` | `/api/integraciones/simular` | Registra una integración simulada (para demo/QA) | — |

Respuestas siguen el formato estándar del repo (`{success, message, data, meta}`).

### Filtros válidos (query params)

- `sistema_externo`: `PagoNet`, `CRMMax`, `NotiSys`, `AnalytixPro`, `VeriCheck`, `WhatsApp`
- `estado`: `pendiente`, `enviado`, `confirmado`, `error`
- `page`, `per_page`: como en `GET /api/clientes`

Filtro inválido → `400`.

---

## 3. Sistemas externos (mocks)

Las integraciones reales no existen en el TP. Cada sistema tiene un **mock** en `utils/` que devuelve una respuesta con la misma forma que tendría la API real. Para producción, reemplazar el mock por un cliente HTTP real:

| Sistema | Archivo | Función principal |
|---|---|---|
| CRMMax | `utils/crmmax.py` | `sync_cliente(cliente)` |
| VeriCheck | `utils/vericheck.py` | `validate_identity(dni, nombre)` |
| NotiSys | `utils/notisys.py` | `enviar_notificacion(tipo, cliente_id, mensaje)` |
| PagoNet | `utils/pagonet.py` | `enviar_facturacion(cliente_id, nombre, plan, monto)` |
| AnalytixPro | _pendiente_ | — |
| WhatsApp | _pendiente_ | — |

---

## 4. Tabla `integracion_externa`

Toda integración (exitosa o fallida) deja registro acá. La tabla ya existía (la creó Equipo 1), Equipo 5 la usa como log de auditoría.

| Columna | Tipo | Valores |
|---|---|---|
| `integracion_id` | PK | — |
| `sistema_externo` | enum | `PagoNet`, `CRMMax`, `NotiSys`, `AnalytixPro`, `VeriCheck`, `WhatsApp` |
| `tipo_evento` | string | ej: `alta_cliente`, `actualizacion_cliente`, `cambio_plan_aprobado`, `solicitud_creada`, `validacion_cambio_critico` |
| `registro_id` | int | ID del registro origen (`cliente_id`, `solicitud_id`, etc.) |
| `tabla_origen` | string | `cliente`, `solicitud`, `simulacion` |
| `estado` | enum | `pendiente`, `enviado`, `confirmado`, `error` |
| `respuesta` | JSONB | Respuesta cruda del sistema externo (o `{error: ...}` si falló) |
| `intentos` | int | Para integraciones con retry (ej. PagoNet) |
| `fecha_creacion` | timestamp | — |

---

## 5. HU cubiertas

| HU | Descripción | Implementación |
|---|---|---|
| HU1 | Envío de facturación a PagoNet | Trigger en cambio de plan en `PUT /api/clientes/<id>` |
| HU2 | Reintento automático de envío a PagoNet | 2 intentos antes de marcar `error` |
| HU3 | Alta automática de clientes en CRMMax | Trigger en `POST /api/clientes` |
| HU4 | Actualización de clientes en CRMMax | Trigger en `PUT /api/clientes/<id>` |
| HU5 | Validación de identidad | VeriCheck antes de cambios críticos |
| HU6 | Bloqueo de cambios no validados | 403 si VeriCheck rechaza |
| HU7 | Confirmación de solicitud creada | NotiSys en `POST /api/solicitudes` |
| HU8 | Seguimiento del estado de solicitudes | NotiSys en `PUT /api/solicitudes/<id>/estado` |
| HU9 | Confirmación de cambio de plan | NotiSys en cambio de `plan_id` |
| HU12 | Consulta de información mediante API | Demo del Equipo 5 |
| HU14 | Registro de comunicaciones externas | Tabla `integracion_externa` |
| HU15 | Consulta del historial | `GET /api/integraciones` |
| HU22 | Monitoreo de errores | `GET /api/integraciones/errores` |

Pendientes: HU10/HU11 (AnalytixPro), HU16–HU20 (WhatsApp), HU21 (configuración de integraciones).

---

## 6. Tests

```bash
pytest tests/test_integraciones.py tests/test_clientes.py tests/test_solicitudes.py -v
```

Mockean la BD, no requieren `.env`.
