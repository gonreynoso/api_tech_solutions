# API Tech Solutions

API REST de **Gestión de Clientes y Servicios** para el proyecto de Consultora Tech Solutions (Análisis y Metodología de Sistemas — Equipo 1).

Stack: **Python + Flask + PostgreSQL (Supabase)**. JWT para autenticación, Flasgger para documentación interactiva (Swagger).

> 📖 Si vas a **consumir** esta API desde otro equipo/proyecto (frontend, otro backend, integraciones), la referencia completa de endpoints, formatos de respuesta y ejemplos está en **[`CONSUMIR_API.md`](./CONSUMIR_API.md)**. Este README es sobre cómo levantar el proyecto, no sobre cómo usar cada endpoint.

---

## ¿Qué resuelve esta API?

Expone operaciones sobre 4 entidades:

- **`usuario`**: cuentas con email/contraseña/rol (`cliente`, `consultor`, `administrador`), autenticación JWT.
- **`cliente`**: perfil de cliente, vinculado 1 a 1 a un `usuario` y a un `plan`.
- **`servicio`**: servicios ofrecidos por la consultora, agrupados por área.
- **`plan`**: planes comerciales (Básico/Profesional/Premium), cada uno con un conjunto de servicios incluidos (tabla intermedia `plan_servicio`).

Todos los listados (`GET`) son públicos. Crear, modificar o borrar requiere un JWT válido.

---

## Estructura del proyecto

```
app.py              # Punto de entrada, registro de blueprints, manejo global de errores
config.py           # Carga de variables de entorno
seed.py             # Script para sembrar datos de prueba
models/             # Acceso a datos (una clase por tabla)
routes/             # Blueprints de Flask (un archivo por recurso)
middleware/auth.py  # Decorador @jwt_required
utils/              # Conexión a DB, respuestas estándar, validaciones
tests/               # Suite de pytest (mockea la DB, no requiere conexión real)
CONSUMIR_API.md     # Referencia completa de endpoints para quien consume la API
```

---

## Cómo levantar el proyecto en tu máquina

### 1. Cloná el repo y entrá a la rama de trabajo

```bash
git clone <url-del-repo>
cd api_tech_solutions
git checkout dev
```

### 2. Creá el entorno virtual e instalá dependencias

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Creá tu archivo `.env`

No se commitea (ya está en `.gitignore`). Pedile a Equipo 1 los datos reales del pooler de Supabase — los compartimos por canal privado, no en el chat del proyecto.

```
DB_HOST=aws-1-sa-east-1.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres.<project_ref>
DB_PASSWORD=<password_real>
JWT_SECRET=<elegí cualquier string largo y random, no necesita coincidir con el de otros equipos>
FLASK_ENV=development
```

> ⚠️ Usá siempre el host del **Connection Pooler** (`*.pooler.supabase.com:6543`), nunca el de conexión directa (`db.*.supabase.co:5432`). La conexión directa de Supabase solo resuelve por IPv6 desde 2024, y la mayoría de las redes (facultad, hogar) no tienen IPv6 — te va a tirar un error de DNS si usás el host equivocado.

### 4. (Opcional) Sembrá datos de prueba

```bash
python seed.py            # inserta datos de ejemplo, no hace nada si ya hay usuarios
python seed.py --reset    # borra TODO y vuelve a sembrar (cuidado: es destructivo)
```

Esto te deja 3 planes, 8 servicios oficiales del caso y 5 usuarios de prueba (admin, consultor y 3 clientes) — detalle completo de credenciales en `CONSUMIR_API.md`.

### 5. Levantá el servidor

```bash
python app.py
```

- API: `http://localhost:5000`
- Documentación interactiva (Swagger): `http://localhost:5000/apidocs/`

---

## Importante: todos pegan contra la misma base

Cada persona corre su **propia instancia local** de la API (`localhost:5000` de cada uno), pero **todas conectan a la misma base de Supabase**. No hay una base por persona ni por equipo.

Consecuencias prácticas:
- Los datos que cree cualquier equipo (un cliente, un servicio) los van a ver todos los demás — es esperado, esa es la fuente de verdad compartida.
- El `JWT_SECRET` de tu `.env` es local a tu instancia: no necesita coincidir con el de nadie más, porque cada instancia genera y valida sus propios tokens.
- Si en algún momento Equipo 6 despliega esto en un servidor real, esa URL pública reemplaza a `localhost:5000` para todos — avisaremos cuando pase.

---

## Correr los tests

```bash
pytest tests/ -v
```

Los tests mockean la base de datos (no necesitás `.env` configurado con credenciales reales para que pasen, aunque sí necesitás las dependencias instaladas).

---

## Convenciones de este repo

- Rama de trabajo: `dev`. Las features nuevas se hacen en una rama propia y se mergean a `dev`.
- Commits agrupados por tema (no un commit gigante por feature).
- Si tocás un endpoint, actualizá también su docstring de Swagger y, si corresponde, `CONSUMIR_API.md`.
