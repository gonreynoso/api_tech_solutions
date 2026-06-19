# CÓMO USAR LA API - GUÍA PARA EQUIPOS 2-7

## 1. INICIAR LA API (Equipo 1)

```bash
cd api_tech_solutions
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

**La API corre en:** `http://localhost:5000`

---

## 2. AUTENTICACIÓN (TODOS LOS EQUIPOS)

### Paso 1: Login

```javascript
const email = "usuario@example.com";
const password = "contraseña123";

const response = await fetch("http://localhost:5000/api/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password })
});

const data = await response.json();

if (data.success) {
  const token = data.data.access_token;
  localStorage.setItem("token", token);
  console.log("✅ Login exitoso");
} else {
  console.error("❌ Login falló:", data.message);
}
```

### Paso 2: Usar el token en TODAS las peticiones

```javascript
const token = localStorage.getItem("token");

const response = await fetch("http://localhost:5000/api/clientes", {
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`  // ← IMPORTANTE
  }
});

const data = await response.json();
console.log(data);
```

**Si el token expira (401):**
```javascript
const response = await fetch("http://localhost:5000/api/auth/refresh", {
  method: "POST",
  headers: { "Authorization": `Bearer ${token}` }
});

const data = await response.json();
if (data.success) {
  localStorage.setItem("token", data.data.access_token);
}
```

---

## 3. EJEMPLOS DE ENDPOINTS

### 3.1 CLIENTES (Equipo 1 + Equipos 3, 4)

#### GET - Listar clientes

```javascript
const token = localStorage.getItem("token");

fetch("http://localhost:5000/api/clientes?page=1&per_page=10", {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  console.log("Clientes:", data.data);
  console.log("Total:", data.pagination.total);
  console.log("Página:", data.pagination.page);
});
```

**Response:**
```json
{
  "success": true,
  "message": "Clientes obtenidos",
  "data": [
    {
      "cliente_id": 1,
      "usuario_id": 5,
      "primer_nombre": "Juan",
      "apellido": "Pérez",
      "dni": "12345678",
      "email": "juan@example.com",
      "plan_id": 2,
      "nombre_plan": "Profesional",
      "creditos": 50
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 45,
    "total_pages": 5
  }
}
```

#### GET - Obtener UN cliente

```javascript
const clienteId = 1;

fetch(`http://localhost:5000/api/clientes/${clienteId}`, {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log(data.data));
```

#### POST - Crear cliente

```javascript
const nuevoCliente = {
  email: "nuevo@example.com",
  password: "Segura123!",
  primer_nombre: "Pedro",
  apellido: "López",
  dni: "87654321",
  codigo_area: "11",
  numero_telefono: "23456789",
  plan_id: 1
};

fetch("http://localhost:5000/api/clientes", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify(nuevoCliente)
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    console.log("✅ Cliente creado. ID:", data.data.cliente_id);
  } else {
    console.error("❌ Error:", data.message, data.errors);
  }
});
```

#### PUT - Actualizar cliente

```javascript
const clienteId = 1;
const cambios = {
  primer_nombre: "Juan Carlos",
  creditos: 75,
  plan_id: 3
};

fetch(`http://localhost:5000/api/clientes/${clienteId}`, {
  method: "PUT",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify(cambios)
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    console.log("✅ Cliente actualizado");
  }
});
```

#### DELETE - Desactivar cliente

```javascript
const clienteId = 1;

fetch(`http://localhost:5000/api/clientes/${clienteId}`, {
  method: "DELETE",
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    console.log("✅ Cliente desactivado");
  }
});
```

---

### 3.2 SERVICIOS (Equipo 1 + Equipos 3, 4)

#### GET - Listar servicios (con filtros)

```javascript
// Sin filtros
fetch("http://localhost:5000/api/servicios", {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log(data.data));

// Con filtro por área
fetch("http://localhost:5000/api/servicios?area=finanzas&page=1", {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log(data.data));
```

**Áreas válidas:**
- finanzas
- marketing
- recursos_humanos
- desarrollo_web
- logistica
- inteligencia_artificial
- gestion_proyectos
- cumplimiento_legal

#### GET - Obtener servicio por ID

```javascript
fetch(`http://localhost:5000/api/servicios/1`, {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log(data.data));
```

#### GET - Servicios de un plan (IMPORTANTE)

```javascript
const planId = 2;

fetch(`http://localhost:5000/api/servicios/by-plan/${planId}`, {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  console.log("Servicios del plan 2:", data.data);
  // Muestra todos los servicios disponibles en ese plan
});
```

#### POST - Crear servicio (admin)

```javascript
const nuevoServicio = {
  nombre_servicio: "Auditoría Financiera",
  descripcion: "Revisión completa de estados financieros",
  area: "finanzas"
};

fetch("http://localhost:5000/api/servicios", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify(nuevoServicio)
})
.then(res => res.json())
.then(data => console.log("Servicio creado. ID:", data.data.servicio_id));
```

#### PUT - Actualizar servicio

```javascript
const servicioId = 1;
const cambios = {
  nombre_servicio: "Auditoría Financiera Avanzada",
  estado_servicio: "activo"
};

fetch(`http://localhost:5000/api/servicios/${servicioId}`, {
  method: "PUT",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify(cambios)
})
.then(res => res.json())
.then(data => console.log("✅ Actualizado"));
```

---

### 3.3 PLANES (Todos)

#### GET - Listar planes

```javascript
fetch("http://localhost:5000/api/planes", {
  headers: { "Authorization": `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  data.data.forEach(plan => {
    console.log(`${plan.nombre_plan}: $${plan.precio} - ${plan.creditos} créditos`);
  });
});
```

**Response:**
```json
{
  "data": [
    {
      "plan_id": 1,
      "nombre_plan": "Basico",
      "precio": "99.99",
      "creditos": 30,
      "tiempo_respuesta": 48,
      "estado_plan": "activo"
    },
    {
      "plan_id": 2,
      "nombre_plan": "Profesional",
      "precio": "299.99",
      "creditos": 100,
      "tiempo_respuesta": 24,
      "estado_plan": "activo"
    }
  ]
}
```

---

## 4. CÓDIGOS DE ERROR

| Código | Significado | Qué hacer |
|--------|-------------|----------|
| 200 | ✅ OK | Todo bien |
| 201 | ✅ Creado | Recurso creado exitosamente |
| 400 | ❌ Bad Request | Falta dato o es inválido. Ver `errors` en response |
| 401 | ❌ No autorizado | Token inválido o expirado. Hacer login de nuevo |
| 404 | ❌ No encontrado | El recurso (cliente, servicio) no existe |
| 500 | ❌ Error del servidor | Problema en la API. Reportar a Equipo 1 |

**Ejemplo de error:**
```json
{
  "success": false,
  "message": "Validación fallida",
  "errors": [
    "email es requerido",
    "plan_id debe ser un número"
  ]
}
```

---

## 5. HELPER FUNCTION (Copiar en tu código)

Para no escribir `fetch()` y headers cada vez:

```javascript
// api.js
class API {
  constructor(baseURL = "http://localhost:5000") {
    this.baseURL = baseURL;
    this.token = localStorage.getItem("token");
  }

  async login(email, password) {
    const res = await fetch(`${this.baseURL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (data.success) {
      this.token = data.data.access_token;
      localStorage.setItem("token", this.token);
    }
    return data;
  }

  async get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = `${this.baseURL}${endpoint}${query ? "?" + query : ""}`;
    
    const res = await fetch(url, {
      headers: { "Authorization": `Bearer ${this.token}` }
    });
    return res.json();
  }

  async post(endpoint, body) {
    const res = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.token}`
      },
      body: JSON.stringify(body)
    });
    return res.json();
  }

  async put(endpoint, body) {
    const res = await fetch(`${this.baseURL}${endpoint}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.token}`
      },
      body: JSON.stringify(body)
    });
    return res.json();
  }

  async delete(endpoint) {
    const res = await fetch(`${this.baseURL}${endpoint}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${this.token}` }
    });
    return res.json();
  }
}

// Uso:
const api = new API();

// Login
await api.login("user@example.com", "password123");

// GET clientes
const clientes = await api.get("/api/clientes", { page: 1, per_page: 10 });
console.log(clientes.data);

// POST cliente
await api.post("/api/clientes", {
  email: "nuevo@example.com",
  password: "Pass123!",
  primer_nombre: "Juan",
  apellido: "Pérez",
  dni: "12345678",
  plan_id: 1
});

// PUT cliente
await api.put("/api/clientes/1", { creditos: 75 });

// DELETE cliente
await api.delete("/api/clientes/1");
```

---

## 6. TESTING CON CURL (Para debug rápido)

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# Copiar el token de la respuesta y usarlo abajo:

# GET clientes
curl http://localhost:5000/api/clientes \
  -H "Authorization: Bearer <TOKEN>"

# POST cliente
curl -X POST http://localhost:5000/api/clientes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "email":"nuevo@example.com",
    "password":"Pass123!",
    "primer_nombre":"Juan",
    "apellido":"Pérez",
    "dni":"12345678",
    "plan_id":1
  }'
```

---

## 7. FLUJO TÍPICO (Equipos 3 y 4 - Frontend)

### Página de Login

```html
<form id="loginForm">
  <input type="email" id="email" placeholder="Email" required>
  <input type="password" id="password" placeholder="Contraseña" required>
  <button type="submit">Entrar</button>
</form>

<script>
const api = new API();

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  
  const response = await api.login(email, password);
  
  if (response.success) {
    console.log("✅ Bienvenido");
    window.location.href = "/dashboard.html";
  } else {
    alert("❌ " + response.message);
  }
});
</script>
```

### Página Dashboard (Listar Clientes)

```html
<div id="clientesList"></div>

<script>
const api = new API();

async function cargarClientes() {
  const response = await api.get("/api/clientes", { page: 1, per_page: 10 });
  
  if (response.success) {
    const html = response.data.map(cliente => `
      <div class="cliente-card">
        <h3>${cliente.primer_nombre} ${cliente.apellido}</h3>
        <p>Email: ${cliente.email}</p>
        <p>DNI: ${cliente.dni}</p>
        <p>Plan: ${cliente.nombre_plan}</p>
        <p>Créditos: ${cliente.creditos}</p>
      </div>
    `).join("");
    
    document.getElementById("clientesList").innerHTML = html;
  } else {
    alert("Error: " + response.message);
  }
}

// Cargar al abrir la página
cargarClientes();
</script>
```

---

## 8. TROUBLESHOOTING

### "401 Unauthorized"
- ✅ El token expiró. Hacer login de nuevo.
- ✅ Olvidaste el `Authorization` header.
- ✅ El token está mal copiado.

### "404 Not Found"
- ✅ El cliente/servicio no existe. Verificar el ID.
- ✅ La URL es incorrecta (falta `/api/` al principio).

### "400 Bad Request"
- ✅ Falta un campo requerido. Ver `errors` en la respuesta.
- ✅ El DNI o email ya existen. Usar otro.

### La API no responde
- ✅ ¿Corriste `python app.py`?
- ✅ ¿Está en `http://localhost:5000`? (No `5001` o `8000`)
- ✅ ¿El .env tiene credenciales correctas de Supabase?

---

## 9. LISTA DE CHEQUEO

- [ ] Equipo 1 corre `python app.py` y la API está en `localhost:5000`
- [ ] Tenés un usuario para testear (o creás uno con POST /api/clientes)
- [ ] Copiaste la clase `API` helper en tu código
- [ ] Hacés login y guardás el token en localStorage
- [ ] Pasás el token en TODOS los fetch() (header `Authorization: Bearer`)
- [ ] Checkeás `response.success` antes de usar `response.data`
