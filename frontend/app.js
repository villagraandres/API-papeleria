"use strict";

const API_STORAGE_KEY = "papeleria-api-url";
const TOKEN_STORAGE_KEY = "papeleria-access-token";
const apiInput = document.querySelector("#api-url");
const notice = document.querySelector("#notice");
const authPanel = document.querySelector("#auth-panel");
const workspace = document.querySelector("#workspace");
let accessToken = localStorage.getItem(TOKEN_STORAGE_KEY);
let currentUser = null;
let currentView = "dashboard";
let noticeTimeout;
let editingProductId = null;
let products = [];
let categories = [];
let clients = [];
let providers = [];

apiInput.value = localStorage.getItem(API_STORAGE_KEY) || apiInput.value;

const entityConfig = {
  productos: {
    title: "Productos",
    singular: "producto",
    description: "Administra los productos y las existencias de tu catálogo.",
    endpoint: "/productos/",
    fields: [
      { name: "nombre", label: "Nombre", required: true, minLength: 2 },
      { name: "descripcion", label: "Descripción", type: "textarea" },
      { name: "precio", label: "Precio", type: "number", min: "0.01", step: "0.01", required: true },
      { name: "stock", label: "Existencias", type: "number", min: "0", step: "1", required: true },
      { name: "stock_minimo", label: "Stock mínimo", type: "number", min: "0", step: "1", value: "5", required: true },
      { name: "categoria_id", label: "Categoría", type: "select", source: "categories", required: true },
    ],
    columns: [
      ["id", "ID"], ["nombre", "Producto"], ["precio", "Precio", value => money(value)],
      ["stock", "Stock"], ["categoria_id", "Categoría", value => categoryName(value)],
    ],
    deactivate: id => `/productos/${id}/desactivar`,
    activate: id => `/productos/${id}/activar`,
    canEdit: true,
    adminOnly: true,
  },
  categorias: {
    title: "Categorías",
    singular: "categoría",
    description: "Organiza los productos con categorías.",
    endpoint: "/categorias/",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "descripcion", label: "Descripción", type: "textarea" },
    ],
    columns: [["id", "ID"], ["nombre", "Nombre"], ["descripcion", "Descripción"]],
    deactivate: id => `/categorias/${id}/desactivar`,
    activate: id => `/categorias/${id}/activar`,
    adminOnly: true,
  },
  clientes: {
    title: "Clientes",
    singular: "cliente",
    description: "Consulta y registra la información de tus clientes.",
    endpoint: "/clientes/",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "correo", label: "Correo", type: "email" },
      { name: "telefono", label: "Teléfono", type: "tel" },
    ],
    columns: [["id", "ID"], ["nombre", "Nombre"], ["correo", "Correo"], ["telefono", "Teléfono"]],
    deactivate: id => `/clientes/${id}/desactivar`,
    activate: id => `/clientes/${id}/activar`,
  },
  proveedores: {
    title: "Proveedores",
    singular: "proveedor",
    description: "Mantén al día la información de tus proveedores.",
    endpoint: "/proveedores/",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "contacto", label: "Persona de contacto" },
      { name: "telefono", label: "Teléfono", type: "tel" },
      { name: "correo", label: "Correo", type: "email" },
    ],
    columns: [["id", "ID"], ["nombre", "Proveedor"], ["contacto", "Contacto"], ["telefono", "Teléfono"], ["correo", "Correo"]],
    deactivate: id => `/proveedores/${id}/desactivar`,
    activate: id => `/proveedores/${id}/activar`,
    adminOnly: true,
  },
};

function apiUrl(path) {
  const base = apiInput.value.trim().replace(/\/+$/, "");
  if (!base) throw new Error("Indica la dirección base de la API.");
  return `${base}${path}`;
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  if (options.body !== undefined) headers.set("Content-Type", "application/json");

  let response;
  try {
    response = await fetch(apiUrl(path), { ...options, headers });
  } catch (error) {
    throw new Error(`No se pudo conectar con la API. Comprueba que esté activa y que la dirección sea correcta. (${error.message})`);
  }

  if (response.status === 204) return null;
  const contentType = response.headers.get("content-type") || "";
  const result = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = typeof result === "object" && result !== null
      ? result.detail || JSON.stringify(result)
      : result;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return result;
}

function showNotice(message, isError = false) {
  window.clearTimeout(noticeTimeout);
  notice.textContent = message;
  notice.classList.toggle("error", isError);
  notice.hidden = false;
  noticeTimeout = window.setTimeout(() => { notice.hidden = true; }, 5000);
}

function money(value) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(Number(value) || 0);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function dateTime(value) {
  return value ? new Date(value).toLocaleString("es-MX", { dateStyle: "short", timeStyle: "short" }) : "—";
}

function setAuthenticated(user) {
  currentUser = user;
  authPanel.hidden = true;
  workspace.hidden = false;
  document.querySelector("#account").hidden = false;
  document.querySelector("#account-name").textContent = `${user.nombre} · ${user.rol}`;
  document.querySelectorAll(".admin-only").forEach(element => {
    element.hidden = user.rol !== "admin";
  });
  renderView(currentView);
}

function clearSession() {
  accessToken = null;
  currentUser = null;
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  authPanel.hidden = false;
  workspace.hidden = true;
  document.querySelector("#account").hidden = true;
}

async function withNotice(action, successMessage) {
  try {
    const result = await action();
    if (successMessage) showNotice(successMessage);
    return result;
  } catch (error) {
    showNotice(error.message, true);
    return undefined;
  }
}

function fieldMarkup(field) {
  const required = field.required ? "required" : "";
  const value = field.value !== undefined ? `value="${escapeHtml(field.value)}"` : "";
  const min = field.min !== undefined ? `min="${field.min}"` : "";
  const step = field.step !== undefined ? `step="${field.step}"` : "";
  const minLength = field.minLength ? `minlength="${field.minLength}"` : "";
  let input;
  if (field.type === "textarea") {
    input = `<textarea name="${field.name}" ${required}></textarea>`;
  } else if (field.type === "select") {
    input = `<select name="${field.name}" data-source="${field.source}" ${required}></select>`;
  } else {
    input = `<input name="${field.name}" type="${field.type || "text"}" ${value} ${min} ${step} ${minLength} ${required}>`;
  }
  return `<label class="field">${escapeHtml(field.label)}${input}</label>`;
}

function renderEntityPage(key) {
  const config = entityConfig[key];
  const root = document.querySelector(`#view-${key}`);
  const canManage = !config.adminOnly || currentUser.rol === "admin";
  const canRestore = Boolean(config.activate) && currentUser.rol === "admin";
  root.innerHTML = `
    <div class="page-heading">
      <div><span class="eyebrow">CATÁLOGO</span><h1>${config.title}</h1><p>${config.description}</p></div>
      <button class="button button-light" data-refresh="${key}" type="button">Actualizar</button>
    </div>
    <div class="management-grid">
      <div class="panel form-panel" ${canManage ? "" : "hidden"}>
        <div class="panel-heading"><div><h2 id="${key}-form-title">Agregar ${config.singular}</h2><p>Completa la información y guarda los cambios.</p></div></div>
        <form id="${key}-form" class="form-grid">
          ${config.fields.map(fieldMarkup).join("")}
          <button class="button button-primary field-wide" type="submit">Guardar registro</button>
          ${config.canEdit ? '<button class="button button-light field-wide" id="cancel-edit" type="button" hidden>Cancelar edición</button>' : ""}
        </form>
        ${canRestore ? `
          <div class="restore-box">
            <p>¿Necesitas reactivar un registro? Escribe su ID.</p>
            <form class="restore-controls" data-restore="${key}">
              <input class="inline-input" name="id" type="number" min="1" placeholder="ID del registro" required aria-label="ID del registro para reactivar">
              <button class="button button-light" type="submit">Reactivar</button>
            </form>
          </div>` : ""}
      </div>
      <div class="panel table-panel">
        <div class="panel-heading"><div><h2>Registros</h2><p id="${key}-count">Cargando datos…</p></div></div>
        <div class="table-wrap" id="${key}-table"></div>
      </div>
    </div>`;
  root.querySelector(`#${key}-form`).addEventListener("submit", event => submitEntity(event, key));
  root.querySelector(`[data-refresh="${key}"]`).addEventListener("click", () => loadEntity(key));
  const restoreForm = root.querySelector(`[data-restore="${key}"]`);
  if (restoreForm) restoreForm.addEventListener("submit", event => restoreEntity(event, key));
  const cancelEdit = root.querySelector("#cancel-edit");
  if (cancelEdit) cancelEdit.addEventListener("click", () => resetProductForm());
}

async function loadOptions() {
  const [productList, categoryList, clientList, providerList] = await Promise.all([
    request("/productos/"), request("/categorias/"), request("/clientes/"), request("/proveedores/"),
  ]);
  products = productList;
  categories = categoryList;
  clients = clientList;
  providers = providerList;
  document.querySelectorAll('select[data-source="categories"]').forEach(select => {
    select.innerHTML = '<option value="">Selecciona una categoría</option>' +
      categories.map(item => `<option value="${item.id}">${escapeHtml(item.nombre)}</option>`).join("");
  });
}

function categoryName(id) {
  return categories.find(item => item.id === Number(id))?.nombre || `#${id}`;
}

async function loadEntity(key) {
  await withNotice(async () => {
    await loadOptions();
    const rows = await request(entityConfig[key].endpoint);
    renderEntityTable(key, rows);
  });
}

function renderEntityTable(key, rows) {
  const config = entityConfig[key];
  const canManage = !config.adminOnly || currentUser.rol === "admin";
  document.querySelector(`#${key}-count`).textContent = `${rows.length} registro${rows.length === 1 ? "" : "s"} activo${rows.length === 1 ? "" : "s"}`;
  const headings = config.columns.map(([, label]) => `<th>${escapeHtml(label)}</th>`).join("");
  const body = rows.map(row => {
    const cells = config.columns.map(([name, , formatter]) => {
      const value = formatter ? formatter(row[name]) : row[name];
      return `<td>${escapeHtml(value ?? "—")}</td>`;
    }).join("");
    const edit = canManage && config.canEdit ? `<button class="button button-light button-small" data-edit="${row.id}" type="button">Editar</button>` : "";
    const deactivate = canManage ? `<button class="button button-danger button-small" data-deactivate="${row.id}" type="button">Desactivar</button>` : "";
    return `<tr>${cells}${canManage ? `<td><div class="table-actions">${edit}${deactivate}</div></td>` : ""}</tr>`;
  }).join("");
  document.querySelector(`#${key}-table`).innerHTML = rows.length
    ? `<table><thead><tr>${headings}${canManage ? "<th>Acciones</th>" : ""}</tr></thead><tbody>${body}</tbody></table>`
    : '<div class="empty-state">No hay registros activos.</div>';
  document.querySelectorAll(`#${key}-table [data-deactivate]`).forEach(button => {
    button.addEventListener("click", () => changeEntityState(key, button.dataset.deactivate, false));
  });
  document.querySelectorAll(`#${key}-table [data-edit]`).forEach(button => {
    button.addEventListener("click", () => editProduct(button.dataset.edit));
  });
}

async function submitEntity(event, key) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form).entries());
  for (const field of entityConfig[key].fields) {
    if (field.type === "number" && data[field.name] !== "") data[field.name] = Number(data[field.name]);
    if (field.type === "select" && data[field.name] !== "") data[field.name] = Number(data[field.name]);
    if (data[field.name] === "") data[field.name] = null;
  }
  const editing = key === "productos" && editingProductId !== null;
  const path = editing ? `/productos/${editingProductId}` : entityConfig[key].endpoint;
  const method = editing ? "PUT" : "POST";
  const completed = await withNotice(() => request(path, { method, body: JSON.stringify(data) }),
    editing ? "Producto actualizado correctamente." : "Registro agregado correctamente.");
  if (completed === undefined) return;
  form.reset();
  if (key === "productos") resetProductForm();
  await loadEntity(key);
}

async function changeEntityState(key, id, activate) {
  const action = activate ? "activar" : "desactivar";
  if (!window.confirm(`¿Deseas ${action} este registro?`)) return;
  const completed = await withNotice(
    () => request(entityConfig[key][activate ? "activate" : "deactivate"](id), { method: "PATCH" }),
    `Registro ${activate ? "activado" : "desactivado"} correctamente.`,
  );
  if (completed !== undefined) await loadEntity(key);
}

async function restoreEntity(event, key) {
  event.preventDefault();
  const form = event.currentTarget;
  const id = new FormData(form).get("id");
  const completed = await withNotice(
    () => request(entityConfig[key].activate(id), { method: "PATCH" }),
    "Registro reactivado correctamente.",
  );
  if (completed !== undefined) {
    form.reset();
    await loadEntity(key);
  }
}

async function editProduct(id) {
  const product = await withNotice(() => request(`/productos/${id}`));
  if (!product) return;
  editingProductId = product.id;
  const form = document.querySelector("#productos-form");
  Object.entries(product).forEach(([name, value]) => {
    const control = form.elements.namedItem(name);
    if (control) control.value = value ?? "";
  });
  document.querySelector("#productos-form-title").textContent = `Editar producto #${product.id}`;
  form.querySelector('[type="submit"]').textContent = "Guardar cambios";
  document.querySelector("#cancel-edit").hidden = false;
  form.scrollIntoView({ behavior: "smooth", block: "center" });
}

function resetProductForm() {
  editingProductId = null;
  const form = document.querySelector("#productos-form");
  if (!form) return;
  form.reset();
  document.querySelector("#productos-form-title").textContent = "Agregar producto";
  form.querySelector('[type="submit"]').textContent = "Guardar registro";
  document.querySelector("#cancel-edit").hidden = true;
}

function renderMovementPage(key) {
  const isSale = key === "ventas";
  const title = isSale ? "Ventas" : "Compras";
  const root = document.querySelector(`#view-${key}`);
  root.innerHTML = `
    <div class="page-heading">
      <div><span class="eyebrow">OPERACIONES</span><h1>${title}</h1><p>${isSale ? "Registra ventas y consulta movimientos de inventario." : "Registra compras y actualiza existencias."}</p></div>
      <button class="button button-light" data-refresh="${key}" type="button">Actualizar</button>
    </div>
    <div class="management-grid">
      <div class="panel form-panel">
        <div class="panel-heading"><div><h2>Nueva ${isSale ? "venta" : "compra"}</h2><p>Agrega uno o más productos al movimiento.</p></div></div>
        <form id="${key}-form" class="form-grid">
          ${isSale
            ? `<label class="field field-wide">Cliente (opcional)<select name="cliente_id"><option value="">Venta sin cliente</option></select></label>`
            : `<label class="field field-wide">Proveedor<select name="proveedor_id" required></select></label>`}
          <div class="field field-wide">
            <span>Productos</span>
            <div class="line-items" id="${key}-items"></div>
            <div class="line-item-toolbar">
              <button class="button button-light button-small" id="${key}-add-item" type="button">+ Agregar producto</button>
              <span class="totals" id="${key}-total"></span>
            </div>
          </div>
          <button class="button button-primary field-wide" type="submit">Registrar ${isSale ? "venta" : "compra"}</button>
        </form>
      </div>
      <div class="panel table-panel">
        <div class="panel-heading"><div><h2>Movimientos</h2><p id="${key}-count">Cargando datos…</p></div></div>
        <form class="filter-row" id="${key}-filters">
          <label class="field">Desde<input type="datetime-local" name="fecha_inicio"></label>
          <label class="field">Hasta<input type="datetime-local" name="fecha_fin"></label>
          <button class="button button-light" type="submit">Filtrar</button>
          <button class="button button-light" id="${key}-clear-filters" type="button">Limpiar</button>
        </form>
        <div class="table-wrap" id="${key}-table"></div>
      </div>
    </div>`;
  const form = root.querySelector(`#${key}-form`);
  form.addEventListener("submit", event => submitMovement(event, key));
  root.querySelector(`[data-refresh="${key}"]`).addEventListener("click", () => loadMovements(key));
  root.querySelector(`#${key}-add-item`).addEventListener("click", () => addMovementItem(key));
  root.querySelector(`#${key}-filters`).addEventListener("submit", event => {
    event.preventDefault();
    loadMovements(key, new FormData(event.currentTarget));
  });
  root.querySelector(`#${key}-clear-filters`).addEventListener("click", () => {
    root.querySelector(`#${key}-filters`).reset();
    loadMovements(key);
  });
  addMovementItem(key);
}

async function loadOptionsForMovement(key) {
  await withNotice(async () => {
    await loadOptions();
    const root = document.querySelector(`#view-${key}`);
    const productOptions = '<option value="">Selecciona un producto</option>' +
      products.map(product => `<option value="${product.id}" data-price="${product.precio}">${escapeHtml(product.nombre)} · ${money(product.precio)} · stock ${product.stock}</option>`).join("");
    root.querySelectorAll(".product-select").forEach(select => { select.innerHTML = productOptions; });
    const clientSelect = root.querySelector('[name="cliente_id"]');
    if (clientSelect) {
      clientSelect.innerHTML = '<option value="">Venta sin cliente</option>' +
        clients.map(client => `<option value="${client.id}">${escapeHtml(client.nombre)}</option>`).join("");
    }
    const providerSelect = root.querySelector('[name="proveedor_id"]');
    if (providerSelect) {
      providerSelect.innerHTML = '<option value="">Selecciona un proveedor</option>' +
        providers.map(provider => `<option value="${provider.id}">${escapeHtml(provider.nombre)}</option>`).join("");
    }
    updateMovementTotal(key);
  });
}

function addMovementItem(key) {
  const isSale = key === "ventas";
  const container = document.querySelector(`#${key}-items`);
  const row = document.createElement("div");
  row.className = `item-row ${isSale ? "no-cost" : ""}`;
  row.innerHTML = `
    <label class="field">Producto<select class="product-select" name="producto_id" required></select></label>
    <label class="field">Cantidad<input name="cantidad" type="number" min="1" step="1" value="1" required></label>
    ${isSale ? "" : '<label class="field cost-field">Costo unitario<input name="costo_unitario" type="number" min="0.01" step="0.01" required></label>'}
    <button class="remove-item" type="button" aria-label="Quitar producto" title="Quitar producto">×</button>`;
  row.querySelector(".product-select").innerHTML = '<option value="">Cargando productos…</option>';
  row.addEventListener("input", () => updateMovementTotal(key));
  row.querySelector(".remove-item").addEventListener("click", () => {
    if (container.children.length === 1) {
      showNotice("Cada movimiento requiere al menos un producto.", true);
      return;
    }
    row.remove();
    updateMovementTotal(key);
  });
  container.append(row);
  if (products.length) {
    row.querySelector(".product-select").innerHTML = '<option value="">Selecciona un producto</option>' +
      products.map(product => `<option value="${product.id}" data-price="${product.precio}">${escapeHtml(product.nombre)} · ${money(product.precio)} · stock ${product.stock}</option>`).join("");
  }
  updateMovementTotal(key);
}

function updateMovementTotal(key) {
  const root = document.querySelector(`#view-${key}`);
  if (!root) return;
  const isSale = key === "ventas";
  let subtotal = 0;
  root.querySelectorAll(".item-row").forEach(row => {
    const quantity = Number(row.querySelector('[name="cantidad"]').value) || 0;
    const select = row.querySelector(".product-select");
    const unitPrice = isSale
      ? Number(select.selectedOptions[0]?.dataset.price) || 0
      : Number(row.querySelector('[name="costo_unitario"]').value) || 0;
    subtotal += quantity * unitPrice;
  });
  const output = root.querySelector(`#${key}-total`);
  if (output) output.textContent = `Subtotal: ${money(subtotal)} · IVA: ${money(subtotal * 0.16)}`;
}

async function submitMovement(event, key) {
  event.preventDefault();
  const isSale = key === "ventas";
  const form = event.currentTarget;
  const items = [...form.querySelectorAll(".item-row")].map(row => {
    const item = {
      producto_id: Number(row.querySelector('[name="producto_id"]').value),
      cantidad: Number(row.querySelector('[name="cantidad"]').value),
    };
    if (!isSale) item.costo_unitario = Number(row.querySelector('[name="costo_unitario"]').value);
    return item;
  });
  const data = { items };
  if (isSale) {
    const clientId = form.elements.namedItem("cliente_id").value;
    data.cliente_id = clientId ? Number(clientId) : null;
  } else {
    data.proveedor_id = Number(form.elements.namedItem("proveedor_id").value);
  }
  const completed = await withNotice(
    () => request(`/${key}/`, { method: "POST", body: JSON.stringify(data) }),
    `${isSale ? "Venta" : "Compra"} registrada correctamente.`,
  );
  if (completed === undefined) return;
  form.reset();
  form.querySelectorAll(".item-row").forEach((row, index) => {
    if (index > 0) row.remove();
    else {
      row.querySelector('[name="cantidad"]').value = "1";
      row.querySelector(".product-select").value = "";
      const cost = row.querySelector('[name="costo_unitario"]');
      if (cost) cost.value = "";
    }
  });
  await loadOptions();
  await loadMovements(key);
  await loadDashboard();
}

async function loadMovements(key, filters = null) {
  await withNotice(async () => {
    const params = new URLSearchParams();
    if (filters) {
      const start = filters.get("fecha_inicio");
      const end = filters.get("fecha_fin");
      if (start) params.set("fecha_inicio", new Date(start).toISOString());
      if (end) params.set("fecha_fin", new Date(end).toISOString());
    }
    const query = params.size ? `?${params}` : "";
    const rows = await request(`/${key}/${query}`);
    renderMovements(key, rows);
  });
}

function renderMovements(key, rows) {
  const isSale = key === "ventas";
  const label = isSale ? "venta" : "compra";
  document.querySelector(`#${key}-count`).textContent = `${rows.length} ${label}${rows.length === 1 ? "" : "s"}`;
  const body = rows.map(row => {
    const partyId = isSale ? row.cliente_id : row.proveedor_id;
    const partyName = isSale
      ? (clients.find(client => client.id === partyId)?.nombre || (partyId ? `Cliente #${partyId}` : "Público general"))
      : (providers.find(provider => provider.id === partyId)?.nombre || `Proveedor #${partyId}`);
    const items = row.items.map(item => {
      const productName = products.find(product => product.id === item.producto_id)?.nombre || `#${item.producto_id}`;
      return `${item.cantidad} × ${productName}`;
    }).join(", ");
    const state = row.estado === "cancelada" ? "cancelada" : "completada";
    const cancelButton = row.estado !== "cancelada"
      ? `<button class="button button-danger button-small" data-cancel="${row.id}" type="button">Cancelar</button>`
      : "";
    return `<tr>
      <td>#${row.id}</td><td>${dateTime(row.created_at)}</td><td>${escapeHtml(partyName)}</td>
      <td>${escapeHtml(items)}</td><td>${money(row.total)}</td>
      <td><span class="badge ${state === "cancelada" ? "cancelled" : ""}">${state}</span></td>
      <td><div class="table-actions">${cancelButton}</div></td>
    </tr>`;
  }).join("");
  document.querySelector(`#${key}-table`).innerHTML = rows.length
    ? `<table><thead><tr><th>ID</th><th>Fecha</th><th>${isSale ? "Cliente" : "Proveedor"}</th><th>Artículos</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>${body}</tbody></table>`
    : '<div class="empty-state">No hay movimientos para mostrar.</div>';
  document.querySelectorAll(`#${key}-table [data-cancel]`).forEach(button => {
    button.addEventListener("click", () => cancelMovement(key, button.dataset.cancel));
  });
}

async function cancelMovement(key, id) {
  if (!window.confirm(`¿Deseas cancelar esta ${key === "ventas" ? "venta" : "compra"}?`)) return;
  const completed = await withNotice(
    () => request(`/${key}/${id}/cancelar`, { method: "PATCH" }),
    `${key === "ventas" ? "Venta" : "Compra"} cancelada correctamente.`,
  );
  if (completed !== undefined) {
    await loadOptions();
    await loadMovements(key);
    await loadDashboard();
  }
}

async function loadUsers() {
  await withNotice(async () => {
    const rows = await request("/autenticacion/usuarios");
    document.querySelector("#usuarios-count").textContent = `${rows.length} usuario${rows.length === 1 ? "" : "s"} registrado${rows.length === 1 ? "" : "s"}`;
    const body = rows.map(user => `<tr>
      <td>${user.id}</td><td>${escapeHtml(user.nombre)}</td><td>${escapeHtml(user.correo)}</td><td>${escapeHtml(user.rol)}</td>
      <td><span class="badge ${user.activo ? "" : "cancelled"}">${user.activo ? "activo" : "inactivo"}</span></td>
      <td>${user.id === currentUser.id ? "Cuenta actual" : `<button class="button button-${user.activo ? "danger" : "light"} button-small" data-user-state="${user.id}" data-active="${user.activo}" type="button">${user.activo ? "Desactivar" : "Activar"}</button>`}</td>
    </tr>`).join("");
    document.querySelector("#usuarios-table").innerHTML = rows.length
      ? `<table><thead><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>${body}</tbody></table>`
      : '<div class="empty-state">No hay usuarios registrados.</div>';
    document.querySelectorAll("#usuarios-table [data-user-state]").forEach(button => {
      button.addEventListener("click", () => changeUserState(button.dataset.userState, button.dataset.active !== "true"));
    });
  });
}

async function changeUserState(id, activate) {
  const state = activate ? "activar" : "desactivar";
  if (!window.confirm(`¿Deseas ${state} este usuario?`)) return;
  const completed = await withNotice(
    () => request(`/autenticacion/usuarios/${id}/${activate ? "activar" : "desactivar"}`, { method: "PATCH" }),
    `Usuario ${activate ? "activado" : "desactivado"} correctamente.`,
  );
  if (completed !== undefined) await loadUsers();
}

function renderUsersPage() {
  const root = document.querySelector("#view-usuarios");
  root.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">ADMINISTRACIÓN</span><h1>Usuarios</h1><p>Consulta las cuentas y cambia su estado de acceso.</p></div>
      <button class="button button-light" id="refresh-users" type="button">Actualizar</button>
    </div>
    <div class="panel table-panel users-page">
      <div class="panel-heading"><div><h2>Cuentas del sistema</h2><p id="usuarios-count">Cargando datos…</p></div></div>
      <div class="table-wrap" id="usuarios-table"></div>
    </div>`;
  root.querySelector("#refresh-users").addEventListener("click", loadUsers);
}

async function loadDashboard() {
  await withNotice(async () => {
    const [productList, categoryList, clientList, providerList] = await Promise.all([
      request("/productos/"), request("/categorias/"), request("/clientes/"), request("/proveedores/"),
    ]);
    products = productList;
    categories = categoryList;
    clients = clientList;
    providers = providerList;
    const cards = [
      ["Productos activos", productList.length, "En el catálogo"],
      ["Categorías", categoryList.length, "Disponibles"],
      ["Clientes", clientList.length, "Registrados"],
      ["Proveedores", providerList.length, "Activos"],
    ];
    document.querySelector("#summary-cards").innerHTML = cards.map(([label, count, note]) =>
      `<article class="summary-card"><span class="summary-label">${label}</span><strong class="summary-value">${count}</strong><span class="summary-note">${note}</span></article>`
    ).join("");
  });
}

async function renderView(key) {
  currentView = key;
  document.querySelectorAll(".view").forEach(view => view.classList.toggle("active", view.id === `view-${key}`));
  document.querySelectorAll(".nav-item[data-view]").forEach(button => button.classList.toggle("active", button.dataset.view === key));
  if (!currentUser) return;
  if (entityConfig[key]) {
    if (!document.querySelector(`#view-${key}`).innerHTML) renderEntityPage(key);
    await loadEntity(key);
  } else if (key === "ventas" || key === "compras") {
    if (!document.querySelector(`#view-${key}`).innerHTML) renderMovementPage(key);
    await loadOptionsForMovement(key);
    await loadMovements(key);
  } else if (key === "usuarios") {
    if (!document.querySelector("#view-usuarios").innerHTML) renderUsersPage();
    await loadUsers();
  } else {
    await loadDashboard();
  }
}

document.querySelector("#navigation").addEventListener("click", event => {
  const button = event.target.closest("[data-view]");
  if (button && !button.hidden) renderView(button.dataset.view);
});
document.querySelector(".content").addEventListener("click", event => {
  const button = event.target.closest(".quick-link[data-view]");
  if (button && !button.hidden) renderView(button.dataset.view);
});
document.querySelector("#refresh-dashboard").addEventListener("click", loadDashboard);

document.querySelector("#save-api").addEventListener("click", async () => {
  localStorage.setItem(API_STORAGE_KEY, apiInput.value.trim().replace(/\/+$/, ""));
  await withNotice(async () => {
    const result = await request("/");
    showNotice(result.message || "Conexión con la API establecida.");
  });
});

document.querySelector("#login-form").addEventListener("submit", async event => {
  event.preventDefault();
  const credentials = Object.fromEntries(new FormData(event.currentTarget).entries());
  const result = await withNotice(() => request("/autenticacion/iniciar-sesion", {
    method: "POST", body: JSON.stringify(credentials),
  }));
  if (!result) return;
  accessToken = result.access_token;
  localStorage.setItem(TOKEN_STORAGE_KEY, accessToken);
  const user = await withNotice(() => request("/autenticacion/perfil"));
  if (!user) {
    clearSession();
    return;
  }
  setAuthenticated(user);
  showNotice(`Bienvenido, ${user.nombre}.`);
});

document.querySelector("#register-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const values = Object.fromEntries(new FormData(form).entries());
  const result = await withNotice(() => request("/autenticacion/registro", {
    method: "POST", body: JSON.stringify({ ...values, rol: "empleado" }),
  }), "Cuenta creada. Ahora puedes iniciar sesión.");
  if (result !== undefined) form.reset();
});

document.querySelector("#logout").addEventListener("click", () => {
  clearSession();
  showNotice("Sesión cerrada.");
});

document.querySelector("#api-url").addEventListener("keydown", event => {
  if (event.key === "Enter") document.querySelector("#save-api").click();
});

async function initialize() {
  if (!accessToken) return;
  const user = await withNotice(() => request("/autenticacion/perfil"));
  if (user) {
    setAuthenticated(user);
  } else {
    clearSession();
  }
}

initialize();
