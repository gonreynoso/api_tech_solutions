const ACCESS_KEY = "equipo5_access";
const REFRESH_KEY = "equipo5_refresh";
const USER_KEY = "equipo5_user";

const $ = (id) => document.getElementById(id);

function escape(value) {
  if (value === null || value === undefined) return "—";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const estadoSesion = $("estadoSesion");
const userBadge = $("userBadge");
const estadoApi = $("estadoApi");
const estadoSimulacion = $("estadoSimulacion");
const tablaClientes = $("tablaClientes");
const tablaLogs = $("tablaLogs");
const selectCliente = $("cliente");

function getAccess() { return localStorage.getItem(ACCESS_KEY); }
function getRefresh() { return localStorage.getItem(REFRESH_KEY); }
function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setSession({ access_token, refresh_token, user }) {
  if (access_token) localStorage.setItem(ACCESS_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  actualizarEstadoSesion();
}

function limpiarSesion() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
  actualizarEstadoSesion();
}

function actualizarEstadoSesion() {
  const user = getUser();
  if (getAccess() && user) {
    estadoSesion.className = "status success";
    estadoSesion.textContent = `Conectado como ${user.email} (rol: ${user.rol}).`;
    userBadge.textContent = user.email;
    userBadge.classList.remove("hidden");
  } else {
    estadoSesion.className = "status";
    estadoSesion.textContent = "Sin sesión activa.";
    userBadge.textContent = "";
    userBadge.classList.add("hidden");
  }
}

async function tryRefresh() {
  const refreshToken = getRefresh();
  if (!refreshToken) return false;
  try {
    const resp = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const data = await resp.json();
    if (resp.ok && data.data && data.data.access_token) {
      setSession({
        access_token: data.data.access_token,
        refresh_token: data.data.refresh_token,
      });
      return true;
    }
  } catch (err) {
    /* ignore, vamos a devolver false */
  }
  limpiarSesion();
  return false;
}

async function apiFetch(url, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const access = getAccess();
  if (access) headers["Authorization"] = `Bearer ${access}`;

  let resp = await fetch(url, { ...options, headers });

  if (resp.status === 401 && getRefresh()) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${getAccess()}`;
      resp = await fetch(url, { ...options, headers });
    }
  }
  return resp;
}

async function login() {
  const email = $("email").value.trim();
  const password = $("password").value;
  if (!email || !password) {
    estadoSesion.className = "status error";
    estadoSesion.textContent = "Email y contraseña son obligatorios.";
    return;
  }

  estadoSesion.className = "status";
  estadoSesion.textContent = "Iniciando sesión...";
  try {
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      estadoSesion.className = "status error";
      estadoSesion.textContent = data.message || "No se pudo iniciar sesión.";
      return;
    }
    setSession({
      access_token: data.data.access_token,
      refresh_token: data.data.refresh_token,
      user: data.data.user,
    });
    $("password").value = "";
    await cargarLogs();
  } catch (err) {
    estadoSesion.className = "status error";
    estadoSesion.textContent = "Error de red al iniciar sesión.";
  }
}

async function cargarClientes() {
  estadoApi.className = "status";
  estadoApi.textContent = "Consultando...";

  try {
    const resp = await apiFetch("/api/clientes");
    const data = await resp.json();
    if (!resp.ok) {
      estadoApi.className = "status error";
      estadoApi.textContent = data.message || "No se pudo consultar la API.";
      return;
    }
    const clientes = data.data || [];
    mostrarClientes(clientes);
    estadoApi.className = "status success";
    estadoApi.textContent = `${clientes.length} clientes (total: ${data.meta?.total ?? clientes.length}).`;
  } catch (err) {
    estadoApi.className = "status error";
    estadoApi.textContent = "Error de red al consultar la API.";
  }
}

function mostrarClientes(clientes) {
  tablaClientes.innerHTML = "";
  selectCliente.innerHTML = '<option value="">Sin cliente</option>';

  if (clientes.length === 0) {
    tablaClientes.innerHTML = '<tr><td colspan="4">No hay clientes disponibles.</td></tr>';
    return;
  }

  for (const c of clientes) {
    const nombre = [c.primer_nombre, c.apellido].filter(Boolean).join(" ") || "—";
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${escape(c.cliente_id)}</td>
      <td>${escape(nombre)}</td>
      <td>${escape(c.dni)}</td>
      <td>${escape(c.plan_id)}</td>
    `;
    tablaClientes.appendChild(fila);

    const option = document.createElement("option");
    option.value = c.cliente_id;
    option.textContent = `${nombre} (#${c.cliente_id})`;
    selectCliente.appendChild(option);
  }
}

async function simularIntegracion() {
  const body = {
    sistema_externo: $("sistema").value,
    tipo_evento: $("tipoEvento").value,
    forzar_error: $("forzarError").checked,
  };
  const clienteId = $("cliente").value;
  if (clienteId) body.cliente_id = parseInt(clienteId, 10);

  estadoSimulacion.className = "status";
  estadoSimulacion.textContent = "Ejecutando...";

  try {
    const resp = await apiFetch("/api/integraciones/simular", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    if (!resp.ok) {
      estadoSimulacion.className = "status error";
      estadoSimulacion.textContent = data.message || "Error en la simulación.";
      return;
    }
    const estado = data.data.estado;
    estadoSimulacion.className = estado === "error" ? "status error" : "status success";
    estadoSimulacion.textContent = `Registrada (id ${data.data.integracion_id}, estado ${estado}).`;
    await cargarLogs();
  } catch (err) {
    estadoSimulacion.className = "status error";
    estadoSimulacion.textContent = "Error de red al simular.";
  }
}

async function cargarLogs() {
  const params = new URLSearchParams();
  const sistema = $("filtroSistema").value;
  const estado = $("filtroEstado").value;
  if (sistema) params.set("sistema_externo", sistema);
  if (estado) params.set("estado", estado);

  try {
    const resp = await apiFetch(`/api/integraciones?${params.toString()}`);
    const data = await resp.json();
    tablaLogs.innerHTML = "";

    if (!resp.ok) {
      tablaLogs.innerHTML = `<tr><td colspan="6">${escape(data.message || "Error al cargar el historial.")}</td></tr>`;
      return;
    }
    if (!data.data || data.data.length === 0) {
      tablaLogs.innerHTML = '<tr><td colspan="6">Sin registros para los filtros seleccionados.</td></tr>';
      return;
    }
    for (const log of data.data) {
      const fecha = (log.fecha_creacion || "").toString().replace("T", " ").slice(0, 19);
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td>${escape(fecha)}</td>
        <td>${escape(log.sistema_externo)}</td>
        <td>${escape(log.tipo_evento)}</td>
        <td>${escape(log.tabla_origen)}</td>
        <td>${escape(log.registro_id)}</td>
        <td><span class="badge ${escape(log.estado)}">${escape(log.estado)}</span></td>
      `;
      tablaLogs.appendChild(fila);
    }
  } catch (err) {
    tablaLogs.innerHTML = '<tr><td colspan="6">Error de red al consultar el historial.</td></tr>';
  }
}

$("btnLogin").addEventListener("click", login);
$("btnLogout").addEventListener("click", limpiarSesion);
$("btnCargarClientes").addEventListener("click", cargarClientes);
$("btnSimular").addEventListener("click", simularIntegracion);
$("btnRecargar").addEventListener("click", cargarLogs);
$("filtroSistema").addEventListener("change", cargarLogs);
$("filtroEstado").addEventListener("change", cargarLogs);

document.querySelectorAll(".cred").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    $("email").value = link.dataset.email;
    $("password").value = link.dataset.password;
  });
});

actualizarEstadoSesion();
cargarClientes();
cargarLogs();
