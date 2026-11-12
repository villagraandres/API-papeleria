// UI sencilla para la API de Papelería PIA (sin frameworks).

const estado = {
  token: localStorage.getItem("token"),
  usuario: null,
  datos: { productos: [], categorias: [], clientes: [], proveedores: [] },
};

const $ = (sel, raiz = document) => raiz.querySelector(sel);
const $$ = (sel, raiz = document) => [...raiz.querySelectorAll(sel)];
const esAdmin = () => estado.usuario?.rol === "admin";
const dinero = (n) => `$${Number(n).toFixed(2)}`;
const fecha = (s) => new Date(s).toLocaleString("es-MX");

// ---------- Utilidades ----------

function avisar(mensaje, error = false) {
  const aviso = $("#aviso");
  aviso.textContent = mensaje;
  aviso.className = error ? "error" : "";
  aviso.hidden = false;
  clearTimeout(avisar.t);
  avisar.t = setTimeout(() => (aviso.hidden = true), 3500);
}

async function api(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (estado.token) opciones.headers.Authorization = `Bearer ${estado.token}`;
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);
  }

  const resp = await fetch(ruta, opciones);
  if (resp.status === 204) return null;
  const datos = await resp.json().catch(() => null);

  if (!resp.ok) {
    if (resp.status === 401 && estado.token) cerrarSesion();
    const detalle = datos?.detail;
    const mensaje = Array.isArray(detalle)
      ? detalle.map((d) => `${d.loc?.at(-1)}: ${d.msg}`).join(" · ")
      : detalle || `Error ${resp.status}`;
    throw new Error(mensaje);
  }
  return datos;
}

// Convierte un formulario a objeto, omitiendo campos vacíos.
function leerFormulario(form) {
  const obj = {};
  for (const [k, v] of new FormData(form)) {
    if (v === "") continue;
    const input = form.elements[k];
    obj[k] = input?.type === "number" || input?.dataset.opciones ? Number(v) : v;
  }
  return obj;
}

// Maneja submit con try/catch y aviso de error.
function alEnviar(form, fn) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await fn(form);
    } catch (err) {
      avisar(err.message, true);
    }
  });
}

function nombreDe(lista, id) {
  return estado.datos[lista].find((x) => x.id === id)?.nombre ?? `#${id}`;
}

// Dibuja una tabla. columnas: [{ titulo, valor: (fila) => texto|Node }]
function tabla(contenedor, filas, columnas) {
  const cont = typeof contenedor === "string" ? $(contenedor) : contenedor;
  cont.innerHTML = "";
  if (!filas.length) {
    cont.innerHTML = '<div class="vacio">Sin registros.</div>';
    return;
  }
  const t = document.createElement("table");
  const cab = t.createTHead().insertRow();
  columnas.forEach((c) => {
    const th = document.createElement("th");
    th.textContent = c.titulo;
    cab.appendChild(th);
  });
  const cuerpo = t.createTBody();
  filas.forEach((f) => {
    const tr = cuerpo.insertRow();
    columnas.forEach((c) => {
      const td = tr.insertCell();
      const v = c.valor(f);
      if (v instanceof Node) td.appendChild(v);
      else td.textContent = v === false ? "" : (v ?? "—");
      if (c.clase) td.className = c.clase;
    });
  });
  cont.appendChild(t);
}

function boton(texto, fn, clase = "secundario chico") {
  const b = document.createElement("button");
  b.textContent = texto;
  b.className = clase;
  b.addEventListener("click", async () => {
    try {
      await fn();
    } catch (err) {
      avisar(err.message, true);
    }
  });
  return b;
}

function acciones(...botones) {
  const span = document.createElement("span");
  span.style.display = "flex";
  span.style.gap = "4px";
  botones.filter(Boolean).forEach((b) => span.appendChild(b));
  return span;
}

function etiqueta(texto, clase = "") {
  const s = document.createElement("span");
  s.className = `etiqueta ${clase}`;
  s.textContent = texto;
  return s;
}

// Llena los <select data-opciones="..."> con los datos cargados.
function llenarSelects() {
  $$("select[data-opciones]").forEach((sel) => {
    const lista = estado.datos[sel.dataset.opciones];
    const actual = sel.value;
    sel.innerHTML = "";
    const vacio = document.createElement("option");
    vacio.value = "";
    vacio.textContent = sel.dataset.vacio || "Selecciona…";
    sel.appendChild(vacio);
    lista.forEach((x) => {
      const o = document.createElement("option");
      o.value = x.id;
      o.textContent = sel.dataset.opciones === "productos"
        ? `${x.nombre} (${dinero(x.precio)} · stock ${x.stock})`
        : x.nombre;
      sel.appendChild(o);
    });
    sel.value = actual;
  });
}

async function cargarCatalogos() {
  const [productos, categorias, clientes, proveedores] = await Promise.all([
    api("GET", "/productos/"),
    api("GET", "/categorias/"),
    api("GET", "/clientes/"),
    api("GET", "/proveedores/"),
  ]);
  Object.assign(estado.datos, { productos, categorias, clientes, proveedores });
  llenarSelects();
}

// ---------- Secciones ----------

const secciones = {
  async productos() {
    tabla("#tabla-productos", estado.datos.productos, [
      { titulo: "ID", valor: (p) => p.id },
      { titulo: "Nombre", valor: (p) => p.nombre },
      { titulo: "Categoría", valor: (p) => nombreDe("categorias", p.categoria_id) },
      { titulo: "Precio", valor: (p) => dinero(p.precio) },
      {
        titulo: "Stock",
        valor: (p) => etiqueta(p.stock, p.stock <= p.stock_minimo ? "bajo" : "ok"),
      },
      { titulo: "Descripción", valor: (p) => p.descripcion },
      {
        titulo: "",
        valor: (p) => esAdmin() && acciones(
          boton("Editar", () => editarProducto(p)),
          boton("Desactivar", async () => {
            await api("PATCH", `/productos/${p.id}/desactivar`);
            avisar("Producto desactivado");
            await recargar();
          }, "peligro chico"),
        ),
      },
    ]);
  },

  async ventas() {
    const f = leerFormulario($("#filtro-ventas"));
    const params = new URLSearchParams();
    if (f.fecha_inicio) params.set("fecha_inicio", `${f.fecha_inicio}T00:00:00`);
    if (f.fecha_fin) params.set("fecha_fin", `${f.fecha_fin}T23:59:59`);
    const ventas = await api("GET", `/ventas/?${params}`);
    tabla("#tabla-ventas", ventas, [
      { titulo: "ID", valor: (v) => v.id },
      { titulo: "Fecha", valor: (v) => fecha(v.created_at) },
      { titulo: "Cliente", valor: (v) => (v.cliente_id ? nombreDe("clientes", v.cliente_id) : "Público general") },
      {
        titulo: "Productos",
        valor: (v) => v.items.map((i) => `${i.cantidad}× ${nombreDe("productos", i.producto_id)}`).join(", "),
      },
      { titulo: "IVA", valor: (v) => dinero(v.iva) },
      { titulo: "Total", valor: (v) => dinero(v.total) },
      { titulo: "Estado", valor: (v) => etiqueta(v.estado, v.estado === "cancelada" ? "bajo" : "ok") },
      {
        titulo: "",
        valor: (v) => v.estado !== "cancelada" && boton("Cancelar", async () => {
          await api("PATCH", `/ventas/${v.id}/cancelar`);
          avisar("Venta cancelada");
          await recargar();
        }, "peligro chico"),
      },
    ]);
  },

  async clientes() {
    tabla("#tabla-clientes", estado.datos.clientes, [
      { titulo: "ID", valor: (c) => c.id },
      { titulo: "Nombre", valor: (c) => c.nombre },
      { titulo: "Correo", valor: (c) => c.correo },
      { titulo: "Teléfono", valor: (c) => c.telefono },
      {
        titulo: "",
        valor: (c) => boton("Desactivar", async () => {
          await api("PATCH", `/clientes/${c.id}/desactivar`);
          avisar("Cliente desactivado");
          await recargar();
        }, "peligro chico"),
      },
    ]);
  },

  async categorias() {
    tabla("#tabla-categorias", estado.datos.categorias, [
      { titulo: "ID", valor: (c) => c.id },
      { titulo: "Nombre", valor: (c) => c.nombre },
      { titulo: "Descripción", valor: (c) => c.descripcion },
      {
        titulo: "",
        valor: (c) => boton("Desactivar", async () => {
          await api("PATCH", `/categorias/${c.id}/desactivar`);
          avisar("Categoría desactivada");
          await recargar();
        }, "peligro chico"),
      },
    ]);
  },

  async proveedores() {
    tabla("#tabla-proveedores", estado.datos.proveedores, [
      { titulo: "ID", valor: (p) => p.id },
      { titulo: "Nombre", valor: (p) => p.nombre },
      { titulo: "Contacto", valor: (p) => p.contacto },
      { titulo: "Teléfono", valor: (p) => p.telefono },
      { titulo: "Correo", valor: (p) => p.correo },
      {
        titulo: "",
        valor: (p) => boton("Desactivar", async () => {
          await api("PATCH", `/proveedores/${p.id}/desactivar`);
          avisar("Proveedor desactivado");
          await recargar();
        }, "peligro chico"),
      },
    ]);
  },

  async compras() {
    const compras = await api("GET", "/compras/");
    tabla("#tabla-compras", compras, [
      { titulo: "ID", valor: (c) => c.id },
      { titulo: "Fecha", valor: (c) => fecha(c.created_at) },
      { titulo: "Proveedor", valor: (c) => nombreDe("proveedores", c.proveedor_id) },
      {
        titulo: "Productos",
        valor: (c) => c.items.map((i) => `${i.cantidad}× ${nombreDe("productos", i.producto_id)}`).join(", "),
      },
      { titulo: "IVA", valor: (c) => dinero(c.iva) },
      { titulo: "Total", valor: (c) => dinero(c.total) },
      { titulo: "Estado", valor: (c) => etiqueta(c.estado, c.estado === "cancelada" ? "bajo" : "ok") },
      {
        titulo: "",
        valor: (c) => c.estado !== "cancelada" && boton("Cancelar", async () => {
          await api("PATCH", `/compras/${c.id}/cancelar`);
          avisar("Compra cancelada");
          await recargar();
        }, "peligro chico"),
      },
    ]);
  },

  async usuarios() {
    const usuarios = await api("GET", "/autenticacion/usuarios");
    tabla("#tabla-usuarios", usuarios, [
      { titulo: "ID", valor: (u) => u.id },
      { titulo: "Nombre", valor: (u) => u.nombre },
      { titulo: "Correo", valor: (u) => u.correo },
      { titulo: "Rol", valor: (u) => u.rol },
      { titulo: "Estado", valor: (u) => etiqueta(u.activo ? "Activo" : "Inactivo", u.activo ? "ok" : "bajo") },
      {
        titulo: "",
        valor: (u) => u.id !== estado.usuario.id && boton(
          u.activo ? "Desactivar" : "Activar",
          async () => {
            await api("PATCH", `/autenticacion/usuarios/${u.id}/${u.activo ? "desactivar" : "activar"}`);
            avisar(u.activo ? "Usuario desactivado" : "Usuario activado");
            await recargar();
          },
          u.activo ? "peligro chico" : "secundario chico",
        ),
      },
    ]);
  },
};

let seccionActual = "productos";

async function mostrar(nombre) {
  seccionActual = nombre;
  $$("[data-vista]").forEach((s) => (s.hidden = s.dataset.vista !== nombre));
  $$("#menu button").forEach((b) => b.classList.toggle("activo", b.dataset.seccion === nombre));
  try {
    await secciones[nombre]();
  } catch (err) {
    avisar(err.message, true);
  }
}

async function recargar() {
  await cargarCatalogos();
  await mostrar(seccionActual);
}

// ---------- Productos: edición ----------

function editarProducto(p) {
  const form = $("#form-producto");
  for (const campo of ["id", "nombre", "descripcion", "precio", "stock", "stock_minimo", "categoria_id"]) {
    form.elements[campo].value = p[campo] ?? "";
  }
  $("#cancelar-edicion").hidden = false;
  form.querySelector("button[type=submit]").textContent = "Actualizar";
  form.scrollIntoView({ behavior: "smooth" });
}

function limpiarFormProducto() {
  const form = $("#form-producto");
  form.reset();
  form.elements.id.value = "";
  $("#cancelar-edicion").hidden = true;
  form.querySelector("button[type=submit]").textContent = "Guardar";
}

// ---------- Partidas (venta / compra) ----------

function agregarPartida(contenedor) {
  const conCosto = contenedor.hasAttribute("data-con-costo");
  const div = document.createElement("div");
  div.className = "partida";
  div.innerHTML = `
    <select data-opciones="productos" required></select>
    <input type="number" min="1" value="1" placeholder="Cantidad" required data-cantidad>
    ${conCosto ? '<input type="number" min="0.01" step="0.01" placeholder="Costo unitario" required data-costo>' : ""}
    <button type="button" class="secundario chico">✕</button>`;
  div.querySelector("button").addEventListener("click", () => {
    if (contenedor.children.length > 1) div.remove();
  });
  contenedor.appendChild(div);
  llenarSelects();
}

function leerPartidas(form) {
  return $$(".partida", form).map((p) => {
    const item = {
      producto_id: Number($("select", p).value),
      cantidad: Number($("[data-cantidad]", p).value),
    };
    const costo = $("[data-costo]", p);
    if (costo) item.costo_unitario = Number(costo.value);
    return item;
  });
}

function reiniciarPartidas(form) {
  form.reset();
  const cont = $(".partidas", form);
  cont.innerHTML = "";
  agregarPartida(cont);
}

// ---------- Sesión ----------

async function iniciarApp() {
  try {
    estado.usuario = await api("GET", "/autenticacion/perfil");
  } catch {
    cerrarSesion();
    return;
  }
  $("#vista-login").hidden = true;
  $("#vista-app").hidden = false;
  $("#nombre-usuario").textContent = `${estado.usuario.nombre} (${estado.usuario.rol})`;
  $$(".solo-admin").forEach((el) => (el.hidden = !esAdmin()));
  $$(".partidas").forEach((c) => {
    c.innerHTML = "";
    agregarPartida(c);
  });
  await cargarCatalogos();
  await mostrar("productos");
}

function cerrarSesion() {
  estado.token = null;
  estado.usuario = null;
  localStorage.removeItem("token");
  $("#vista-app").hidden = true;
  $("#vista-login").hidden = false;
}

// ---------- Eventos ----------

alEnviar($("#form-login"), async (form) => {
  const { access_token } = await api("POST", "/autenticacion/iniciar-sesion", leerFormulario(form));
  estado.token = access_token;
  localStorage.setItem("token", access_token);
  form.reset();
  await iniciarApp();
});

alEnviar($("#form-registro"), async (form) => {
  await api("POST", "/autenticacion/registro", leerFormulario(form));
  avisar("Cuenta creada. Ahora inicia sesión.");
  form.reset();
  $("#form-registro").hidden = true;
  $("#form-login").hidden = false;
});

$("#link-registro").addEventListener("click", (e) => {
  e.preventDefault();
  $("#form-login").hidden = true;
  $("#form-registro").hidden = false;
});
$("#link-login").addEventListener("click", (e) => {
  e.preventDefault();
  $("#form-registro").hidden = true;
  $("#form-login").hidden = false;
});

$("#btn-salir").addEventListener("click", cerrarSesion);
$$("#menu button").forEach((b) => b.addEventListener("click", () => mostrar(b.dataset.seccion)));

alEnviar($("#form-producto"), async (form) => {
  const { id, ...datos } = leerFormulario(form);
  if (id) {
    await api("PUT", `/productos/${id}`, datos);
    avisar("Producto actualizado");
  } else {
    await api("POST", "/productos/", datos);
    avisar("Producto creado");
  }
  limpiarFormProducto();
  await recargar();
});
$("#cancelar-edicion").addEventListener("click", limpiarFormProducto);

alEnviar($("#form-cliente"), async (form) => {
  await api("POST", "/clientes/", leerFormulario(form));
  form.reset();
  avisar("Cliente agregado");
  await recargar();
});

alEnviar($("#form-categoria"), async (form) => {
  await api("POST", "/categorias/", leerFormulario(form));
  form.reset();
  avisar("Categoría agregada");
  await recargar();
});

alEnviar($("#form-proveedor"), async (form) => {
  await api("POST", "/proveedores/", leerFormulario(form));
  form.reset();
  avisar("Proveedor agregado");
  await recargar();
});

alEnviar($("#form-usuario"), async (form) => {
  await api("POST", "/autenticacion/registro-admin", { ...leerFormulario(form), rol: "admin" });
  form.reset();
  avisar("Administrador creado");
  await recargar();
});

alEnviar($("#form-venta"), async (form) => {
  const clienteId = form.elements.cliente_id.value;
  const venta = await api("POST", "/ventas/", {
    cliente_id: clienteId ? Number(clienteId) : null,
    items: leerPartidas(form),
  });
  avisar(`Venta #${venta.id} registrada · Total ${dinero(venta.total)}`);
  reiniciarPartidas(form);
  await recargar();
});

alEnviar($("#form-compra"), async (form) => {
  const compra = await api("POST", "/compras/", {
    proveedor_id: Number(form.elements.proveedor_id.value),
    items: leerPartidas(form),
  });
  avisar(`Compra #${compra.id} registrada · Total ${dinero(compra.total)}`);
  reiniciarPartidas(form);
  await recargar();
});

alEnviar($("#filtro-ventas"), () => mostrar("ventas"));

$$("[data-agregar-partida]").forEach((b) =>
  b.addEventListener("click", () => agregarPartida($(".partidas", b.closest("form")))),
);

// Arranque
if (estado.token) iniciarApp();
else cerrarSesion();
