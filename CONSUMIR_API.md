# Cómo consumir la API — Guía para equipos / trainees

Esta guía documenta la API tal como está implementada **hoy** en el código (`app.py`, `routes/`, `models/`). Si encontrás una diferencia entre esta guía y el comportamiento real, el código manda — avisá para corregir el doc.

Esta API la construyó el **Equipo 1** (Gestión de Clientes y Servicios). Es la fuente de verdad para todo lo relacionado a `cliente`, `servicio`, `plan` y `usuario`.

## ¿Quién necesita leer qué?

No todos los equipos consumen esta API. Si te asignaron este doc, buscá tu equipo:

| Equipo | Tarea | ¿Necesita esta API? | Qué leer |
|---|---|---|---|
| **Equipo 1** (nosotros) | Gestión de Clientes y Servicios | Son los dueños | Todo, son quienes la mantienen |
| **Equipo 2** | Gestión de Solicitudes y Reportes (PHP + Airtable) | Solo si necesitan datos de clientes/servicios desde su sistema | Secciones 2 a 5 (auth y endpoints), no necesitan el helper JS |
| **Equipo 3** | Panel de Clientes (frontend) | **Sí, totalmente** | Todo el documento, sobre todo secciones 2, 3.1, 3.3 y 6 |
| **Equipo 4** | Panel de Administrador (frontend) | **Sí, totalmente** | Todo, con foco en los endpoints protegidos (`POST`/`PUT`/`DELETE` y `/api/usuarios`) |
| **Equipo 5** | Integración con otros sistemas (JS + PHP) | Sí, si integran clientes/servicios/planes con sistemas externos | Secciones 2 a 6 |
| **Equipo 6** | Seguridad y Despliegue | Sí, pero no los endpoints | Sección 1 (`.env`, `JWT_SECRET`, pooler de Supabase) y sección 5 (códigos de error) |
| **Equipo 7** | Caso Azul Farmacia | No, es un caso aparte | No aplica |

Si tu equipo no aparece en "Sí" arriba y alguien te mandó este doc, probablemente sea porque van a consumir datos de clientes/servicios desde su propio sistema — confirmá con Equipo 1 antes de asumir que necesitás todo el archivo.

---

## 0. Antes de arrancar: lo que esta API NO hace

Para evitar confusiones comunes de trainees:

- **No hay endpoint de registro/signup público.** No existe ningún `POST /api/auth/register`. Para que alguien pueda loguearse, tiene que existir antes una fila en la tabla `usuario` (creada por seed, por un admin directamente en la base, o a futuro por un endpoint que no existe todavía).
- **`POST /api/clientes` NO crea un usuario ni una contraseña.** Crea solo el perfil de cliente (nombre, DNI, plan, etc.) y necesita que le pases un `usuario_id` que **ya exista** en la tabla `usuario`. Si querés un cliente que pueda loguearse, primero necesitás un usuario.
- **Los listados de `clientes`, `servicios` y `planes` son públicos** (no requieren token). Solo las operaciones de escritura (`POST`/`PUT`/`DELETE`) y `GET /api/usuarios` requieren JWT.
- Los nombres de columnas en las respuestas son los de la base real, en español y sin tildes: `primer_nombre`, `nombre_servicio`, `nombre_plan`, `estado_servicio`, etc. No vas a ver `nombre`, `name`, ni `status`.

---

## 1. Levantar la API localmente

```bash
cd api_tech_solutions
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows (cmd o PowerShell)
.venv\Scripts\activate

pip install -r requirements.txt
```

Creá un archivo `.env` en la raíz (no lo subas a git, ya está en `.gitignore`) basado en `env.example.txt`:

```
DB_HOST=aws-1-sa-east-1.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres.<tu_project_ref>
DB_PASSWORD=<password_real>
JWT_SECRET=<algo_largo_y_random>
FLASK_ENV=development
```

> ⚠️ Usá el **Connection Pooler** de Supabase (`*.pooler.supabase.com:6543`), no el host de conexión directa (`db.*.supabase.co:5432`). Muchas redes (incluida la de la facultad/casa) no tienen IPv6, y la conexión directa de Supabase solo resuelve por IPv6 desde 2024 — vas a tirar `could not translate host name` si usás el host directo.

Si las tablas están vacías, sembrá datos de prueba:

```bash
python seed.py            # inserta datos, no hace nada si ya hay usuarios
python seed.py --reset    # borra todo y vuelve a sembrar
```

Esto crea 3 planes, 8 servicios, y 4 usuarios de prueba (ver tabla abajo). Después corré:

```bash
python app.py
```

**La API corre en:** `http://localhost:5000`
**Swagger / documentación interactiva:** `http://localhost:5000/apidocs/`

Usá Swagger para explorar y probar cada endpoint con "Try it out" — es la forma más rápida de validar que tu request está bien formado antes de escribir código.

### Usuarios de prueba (creados por `seed.py`)

| Email | Password | Rol |
|---|---|---|
| `admin@techsolutions.com` | `Password123` | administrador |
| `consultor@techsolutions.com` | `Password123` | consultor |
| `cliente1@techsolutions.com` | `Password123` | cliente (plan Básico) |
| `cliente2@techsolutions.com` | `Password123` | cliente (plan Premium) |

---

## 2. Forma de las respuestas (IMPORTANTE, leer antes de programar)

**Todas** las respuestas tienen esta forma base:

```json
{
  "success": true,
  "message": "OK",
  "data": { ... } 
}
```

- `success`: `true` o `false`. Revisá esto antes de tocar `data`.
- `message`: texto humano, no parsear lógica sobre esto.
- `data`: el contenido real. Puede ser un objeto, un array, o `null`.

Cuando hay **paginación** (solo en `GET /api/clientes`), aparece además una clave `meta`, **no** `pagination`:

```json
{
  "success": true,
  "message": "OK",
  "data": [ /* array de clientes */ ],
  "meta": { "page": 1, "per_page": 20, "total": 45 }
}
```

Cuando hay **error**, `success` es `false` y puede venir una clave `errors` con detalle (forma libre, no siempre es un array):

```json
{
  "success": false,
  "message": "Faltan campos requeridos",
  "errors": { "missing": ["primer_nombre", "dni"] }
}
```

---

## 3. Autenticación

### 3.1 Login

```
POST /api/auth/login
Content-Type: application/json
```

**Body:**
```json
{ "email": "cliente1@techsolutions.com", "password": "Password123" }
```

**Respuesta 200:**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "user": { "usuario_id": 3, "email": "cliente1@techsolutions.com", "rol": "cliente" }
  }
}
```

**Errores posibles:** `400` (faltan campos o email mal formado), `401` (credenciales inválidas).

El `access_token` expira en **24 horas** (configurable por `JWT_ACCESS_EXPIRES_HOURS` en `.env`). El `refresh_token` expira en 30 días por default.

### 3.2 Usar el token

En **cada** request a un endpoint protegido, mandá el header:

```
Authorization: Bearer <access_token>
```

Sin el prefijo `Bearer ` (con un espacio después) la API responde `401 - Token no provisto`, aunque el token en sí sea válido.

### 3.3 Refrescar el token

Cuando el `access_token` expira (vas a ver `401`), no hagas login de nuevo — usá el refresh:

```
POST /api/auth/refresh
Content-Type: application/json
```

**Body:**
```json
{ "refresh_token": "eyJhbGciOi..." }
```

**Respuesta 200:** mismo formato que login, con `access_token` y `refresh_token` nuevos (el refresh token también se renueva, guardá el nuevo).

**Errores:** `400` (falta `refresh_token`), `401` (expirado, inválido, o es un access_token usado donde se espera un refresh_token), `404` (el usuario fue borrado).

---

## 4. Endpoints

### Resumen de protección

| Endpoint | Método | Requiere JWT |
|---|---|---|
| `/api/auth/login` | POST | No |
| `/api/auth/refresh` | POST | No |
| `/api/clientes` | GET | **No** |
| `/api/clientes/{id}` | GET | **No** |
| `/api/clientes` | POST | **Sí** |
| `/api/clientes/{id}` | PUT | **Sí** |
| `/api/clientes/{id}` | DELETE | **Sí** |
| `/api/servicios` | GET | **No** |
| `/api/servicios/{id}` | GET | **No** |
| `/api/servicios/by-plan/{plan_id}` | GET | **No** |
| `/api/servicios` | POST | **Sí** |
| `/api/servicios/{id}` | PUT | **Sí** |
| `/api/planes` | GET | **No** |
| `/api/planes/{id}` | GET | **No** |
| `/api/usuarios` | GET | **Sí** |
| `/api/usuarios/{id}` | GET | **Sí** |

---

### 4.1 Clientes

#### `GET /api/clientes` — listar (con paginación)

Query params opcionales: `page` (default 1), `per_page` (default 20).

```bash
curl "http://localhost:5000/api/clientes?page=1&per_page=10"
```

**Respuesta 200:**
```json
{
  "success": true,
  "message": "OK",
  "data": [
    {
      "cliente_id": 1,
      "usuario_id": 3,
      "primer_nombre": "Lucia",
      "segundo_nombre": null,
      "apellido": "Fernandez",
      "segundo_apellido": null,
      "dni": "30111222",
      "codigo_pais": "54",
      "codigo_area": "11",
      "numero_telefono": "41234567",
      "fecha_alta": "2026-06-19",
      "creditos": 5,
      "plan_id": 1,
      "email": "cliente1@techsolutions.com",
      "estado": "activo",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "meta": { "page": 1, "per_page": 10, "total": 2 }
}
```

Notá que `email` y `estado` vienen del JOIN con `usuario` — esas columnas no existen en la tabla `cliente`.

#### `GET /api/clientes/{cliente_id}` — detalle

```bash
curl http://localhost:5000/api/clientes/1
```

`404` si no existe.

#### `POST /api/clientes` — crear (requiere JWT)

El `usuario_id` que mandes **tiene que existir previamente** en `usuario`. Esta API no crea el usuario por vos.

```bash
curl -X POST http://localhost:5000/api/clientes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "usuario_id": 5,
    "primer_nombre": "Pedro",
    "apellido": "Lopez",
    "dni": "87654321",
    "plan_id": 1,
    "codigo_pais": "54",
    "codigo_area": "11",
    "numero_telefono": "23456789",
    "creditos": 0
  }'
```

Campos requeridos: `usuario_id`, `primer_nombre`, `apellido`, `dni`, `plan_id`.
Opcionales: `segundo_nombre`, `segundo_apellido`, `codigo_pais`, `codigo_area`, `numero_telefono`, `creditos` (default 0).

`201` si se creó. `400` si faltan campos. `401` sin token válido.

#### `PUT /api/clientes/{cliente_id}` — actualizar (requiere JWT)

Mismos campos requeridos que el POST, **menos** `usuario_id` (no se puede reasignar el usuario de un cliente desde este endpoint).

```bash
curl -X PUT http://localhost:5000/api/clientes/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"primer_nombre":"Lucia","apellido":"Fernandez","dni":"30111222","plan_id":2}'
```

`404` si el cliente no existe.

#### `DELETE /api/clientes/{cliente_id}` — desactivar (requiere JWT)

No borra la fila: pone `usuario.estado = 'inactivo'` para el usuario asociado a ese cliente. Por eso después de esto, ese usuario **tampoco va a poder loguearse** (el login filtra por `estado = 'activo'`).

```bash
curl -X DELETE http://localhost:5000/api/clientes/1 -H "Authorization: Bearer <TOKEN>"
```

---

### 4.2 Servicios

#### `GET /api/servicios` — listar con filtros opcionales

Query params: `area`, `estado`.

**Valores válidos de `area`:** `finanzas`, `marketing`, `recursos_humanos`, `desarrollo_web`, `logistica`, `inteligencia_artificial`, `gestion_proyectos`, `cumplimiento_legal`. Mandar cualquier otro valor no rompe la request (no hay validación en la API), pero la fila nunca va a existir en la base por la constraint `CHECK` de Postgres si intentás crear un servicio con un área inválida — ahí sí te va a fallar el `POST`/`PUT` con un error de base de datos.

```bash
curl "http://localhost:5000/api/servicios?area=finanzas&estado=activo"
```

#### `GET /api/servicios/{servicio_id}` — detalle

`404` si no existe.

#### `GET /api/servicios/by-plan/{plan_id}` — servicios incluidos en un plan

Resuelve la relación a través de la tabla intermedia `plan_servicio`.

```bash
curl http://localhost:5000/api/servicios/by-plan/2
```

#### `POST /api/servicios` — crear (requiere JWT)

```bash
curl -X POST http://localhost:5000/api/servicios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "nombre_servicio": "Auditoria Financiera",
    "descripcion": "Revision completa de estados financieros",
    "area": "finanzas"
  }'
```

Campos requeridos: `nombre_servicio`, `descripcion`, `area`. Opcional: `estado_servicio` (default `"activo"`).

#### `PUT /api/servicios/{servicio_id}` — actualizar (requiere JWT)

Acá `estado_servicio` **sí es requerido** (a diferencia del POST).

```bash
curl -X PUT http://localhost:5000/api/servicios/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "nombre_servicio": "Auditoria Financiera Avanzada",
    "descripcion": "Revision completa con dictamen",
    "area": "finanzas",
    "estado_servicio": "activo"
  }'
```

---

### 4.3 Planes

#### `GET /api/planes` — listar (público, sin token)

```bash
curl http://localhost:5000/api/planes
```

**Respuesta 200:**
```json
{
  "success": true,
  "message": "OK",
  "data": [
    { "plan_id": 1, "nombre_plan": "Basico", "precio": "9999.00", "creditos": 10, "tiempo_respuesta": 72, "estado_plan": "activo", "created_at": "...", "updated_at": "..." },
    { "plan_id": 2, "nombre_plan": "Profesional", "precio": "24999.00", "creditos": 30, "tiempo_respuesta": 24, "estado_plan": "activo", "created_at": "...", "updated_at": "..." },
    { "plan_id": 3, "nombre_plan": "Premium", "precio": "49999.00", "creditos": 100, "tiempo_respuesta": 4, "estado_plan": "activo", "created_at": "...", "updated_at": "..." }
  ]
}
```

`precio` viene como **string** (ej. `"9999.00"`), porque Postgres lo guarda como `NUMERIC` y psycopg2 lo serializa así. Si necesitás hacer cuentas, convertilo a número en tu código (`parseFloat(plan.precio)` en JS, `Decimal(plan["precio"])` en Python), no asumas que ya es number.

No hay endpoints `POST`/`PUT`/`DELETE` para planes todavía — se gestionan directo en la base.

#### `GET /api/planes/{plan_id}` — detalle (público)

`404` si no existe.

---

### 4.4 Usuarios (requiere JWT, todos los endpoints)

Pensado para administración. **Nunca** devuelve `contraseña` ni `token_jwt`, ni aunque seas admin.

#### `GET /api/usuarios` — listar

```bash
curl http://localhost:5000/api/usuarios -H "Authorization: Bearer <TOKEN>"
```

**Respuesta 200:**
```json
{
  "success": true,
  "message": "OK",
  "data": [
    { "usuario_id": 1, "email": "admin@techsolutions.com", "rol": "administrador", "estado": "activo", "ultimo_acceso": "...", "created_at": "..." }
  ]
}
```

#### `GET /api/usuarios/{usuario_id}` — detalle

`404` si no existe.

---

## 5. Códigos de estado HTTP

| Código | Significado | Qué hacer |
|---|---|---|
| 200 | OK | Todo bien |
| 201 | Creado | El POST creó el recurso, mirá `data` para el ID nuevo |
| 400 | Bad Request | Falta un campo requerido o es inválido (email mal formado). Mirá `errors` |
| 401 | No autorizado | Token ausente, mal formado, expirado, o credenciales inválidas en login |
| 404 | No encontrado | El cliente/servicio/plan/usuario con ese ID no existe |
| 500 | Error interno | Bug en la API o error de query. Reportalo con el endpoint y body exactos |
| 503 | Servicio no disponible | La API no pudo conectarse a Supabase. No es tu código — reintentá en un rato o avisá |

**Importante:** `400` con campos faltantes te devuelve la lista exacta en `errors.missing`, no tengas que adivinar:

```json
{ "success": false, "message": "Faltan campos requeridos", "errors": { "missing": ["primer_nombre", "dni"] } }
```

---

## 6. Helper de JavaScript (fetch)

```javascript
// api.js
class API {
  constructor(baseURL = "http://localhost:5000") {
    this.baseURL = baseURL;
    this.token = localStorage.getItem("access_token");
    this.refreshToken = localStorage.getItem("refresh_token");
  }

  async login(email, password) {
    const res = await fetch(`${this.baseURL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (data.success) {
      this.token = data.data.access_token;
      this.refreshToken = data.data.refresh_token;
      localStorage.setItem("access_token", this.token);
      localStorage.setItem("refresh_token", this.refreshToken);
    }
    return data;
  }

  async refresh() {
    const res = await fetch(`${this.baseURL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: this.refreshToken }),
    });
    const data = await res.json();
    if (data.success) {
      this.token = data.data.access_token;
      this.refreshToken = data.data.refresh_token;
      localStorage.setItem("access_token", this.token);
      localStorage.setItem("refresh_token", this.refreshToken);
    }
    return data;
  }

  // request() reintenta una vez con refresh si recibe 401
  async request(method, endpoint, body) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.token}` },
    };
    if (body !== undefined) opts.body = JSON.stringify(body);

    let res = await fetch(`${this.baseURL}${endpoint}`, opts);

    if (res.status === 401 && this.refreshToken) {
      const refreshed = await this.refresh();
      if (refreshed.success) {
        opts.headers["Authorization"] = `Bearer ${this.token}`;
        res = await fetch(`${this.baseURL}${endpoint}`, opts);
      }
    }
    return res.json();
  }

  get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request("GET", `${endpoint}${query ? "?" + query : ""}`);
  }
  post(endpoint, body) { return this.request("POST", endpoint, body); }
  put(endpoint, body) { return this.request("PUT", endpoint, body); }
  delete(endpoint) { return this.request("DELETE", endpoint); }
}

// Uso:
const api = new API();
await api.login("cliente1@techsolutions.com", "Password123");

const clientes = await api.get("/api/clientes", { page: 1, per_page: 10 });
console.log(clientes.data);

const planes = await api.get("/api/planes"); // no necesita estar logueado, pero no hace daño
console.log(planes.data);

await api.post("/api/servicios", {
  nombre_servicio: "Soporte IT",
  descripcion: "Soporte tecnico 24/7",
  area: "desarrollo_web",
});
```

> `GET` no manda body — si llamás `api.get(...)` no pongas un tercer argumento de body, `request()` no lo va a mandar si es `undefined`.

---

## 7. Testing rápido con curl

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@techsolutions.com","password":"Password123"}'

# Guardá el access_token de la respuesta y usalo:
TOKEN="<pegar_access_token_aca>"

# Endpoints públicos, sin token
curl http://localhost:5000/api/planes
curl http://localhost:5000/api/clientes
curl http://localhost:5000/api/servicios

# Endpoint protegido
curl http://localhost:5000/api/usuarios -H "Authorization: Bearer $TOKEN"

# Crear servicio (protegido)
curl -X POST http://localhost:5000/api/servicios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"nombre_servicio":"Soporte IT","descripcion":"Soporte 24/7","area":"desarrollo_web"}'
```

---

## 8. Troubleshooting

**"401 Unauthorized" en un endpoint protegido**
- Te olvidaste el header `Authorization: Bearer <token>`.
- El token expiró (24hs) — usá `/api/auth/refresh`, no hagas login de nuevo si todavía tenés el refresh token.
- Te falta el espacio entre `Bearer` y el token, o pegaste el token incompleto.

**"401 Unauthorized" en login**
- Email o contraseña incorrectos, o el usuario tiene `estado != 'activo'`.
- Estás probando con un email que no existe — corré `python seed.py` si la base está vacía.

**"404 Not Found"**
- El ID no existe en esa tabla. Para clientes/servicios/planes verificá con el `GET` de listado primero.
- Te falta `/api/` al principio de la URL, o usaste un método HTTP que no existe en esa ruta (revisá la tabla de la sección 4).

**"400 Bad Request" al crear/actualizar**
- Mirá `errors.missing` en la respuesta — te dice exactamente qué campo falta.
- En clientes: ¿el `usuario_id` que mandaste existe de verdad en la tabla `usuario`? Si no existe, la base va a rechazar el INSERT por la foreign key y te va a llegar un `500`, no un `400` (la API no valida la FK antes de pegarle a la base).

**"500 Internal Server Error" / "503 Service Unavailable"**
- `503` = no se pudo conectar a Supabase. Revisá que el `.env` tenga el host del **pooler**, no el de conexión directa.
- `500` = la query falló por otra razón (constraint violada, columna mal escrita, etc.). Reportalo con el body exacto que mandaste.

**La API no responde / "Connection refused"**
- ¿Corriste `python app.py`? ¿Está escuchando en el puerto 5000?
- ¿Estás pegándole a `http://localhost:5000` y no a otro puerto?

---

## 9. Checklist antes de pedir ayuda

- [ ] `python app.py` corriendo y sin errores en la consola
- [ ] Probaste el endpoint primero en `/apidocs/` (Swagger) antes de escribir código
- [ ] Hiciste login y tenés un `access_token` válido guardado
- [ ] Mandás `Authorization: Bearer <token>` en los endpoints que lo requieren (ver tabla sección 4)
- [ ] Revisaste `response.success` antes de leer `response.data`
- [ ] Si es un POST a `/api/clientes`, confirmaste que el `usuario_id` ya existe
- [ ] Leíste el mensaje de `errors` completo antes de asumir qué está mal

---





