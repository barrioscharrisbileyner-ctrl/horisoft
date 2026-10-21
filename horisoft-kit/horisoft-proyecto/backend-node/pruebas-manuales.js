/**
 * Pruebas manuales de HORISOFT
 * ------------------------------------------------------------------
 * Ejecuta este archivo con:  node pruebas-manuales.js
 *
 * Simula peticiones HTTP (req/res) contra los controladores reales,
 * sin necesitar Postman ni tener el servidor corriendo. Sirve para
 * demostrar en segundos que las reglas de negocio de los 14 módulos
 * funcionan correctamente (creación, consulta, actualización,
 * eliminación y validaciones que deben fallar a propósito).
 * ------------------------------------------------------------------
 */

const { llamar } = require("./test-harness");

// Fecha de reserva calculada (no fija): una fecha escrita a mano termina quedando en el
// pasado y la regla "no reservar en fechas pasadas" hace fallar la prueba (ver INC-03).
const _ahora = new Date();
const FECHA_FUTURA = new Date(_ahora.getTime() - _ahora.getTimezoneOffset() * 60000 + 7 * 24 * 60 * 60 * 1000)
    .toISOString().split("T")[0];

require("dotenv").config(); // authService.js exige JWT_SECRET; este archivo no pasa por app.js.

const zonasCtrl = require("./controllers/zonasComunes.controller");
const reservasCtrl = require("./controllers/reservas.controller");
const vigilantesCtrl = require("./controllers/vigilantes.controller");
const visitantesCtrl = require("./controllers/visitantes.controller");
const authCtrl = require("./controllers/authController");
const pqrCtrl = require("./controllers/pqr.controller");
const comunicadosCtrl = require("./controllers/comunicados.controller");
const cuentasCtrl = require("./controllers/cuentasCobro.controller");
const pagosCtrl = require("./controllers/pagos.controller");
const proveedoresCtrl = require("./controllers/proveedores.controller");
const inventarioCtrl = require("./controllers/inventario.controller");
const vehiculosCtrl = require("./controllers/vehiculos.controller");
const documentosCtrl = require("./controllers/documentos.controller");
const configuracionCtrl = require("./controllers/configuracion.controller");

console.log("\n========== MODULO: ZONAS COMUNES ==========");
llamar("GET /zonas-comunes", zonasCtrl, "listar", { query: {} });
llamar("POST /zonas-comunes (crear cancha de tenis)", zonasCtrl, "crear", {
    body: { nombre: "Cancha de Tenis", descripcion: "Cancha techada", capacidad: 4, costo_reserva: 20000 },
});
llamar("POST /zonas-comunes (falta capacidad -> error)", zonasCtrl, "crear", {
    body: { nombre: "Zona sin capacidad" },
});

console.log("\n========== MODULO: RESERVAS ==========");
llamar("POST /reservas (reserva valida)", reservasCtrl, "crear", {
    body: { id_zona: 1, id_residencia: 101, fecha: FECHA_FUTURA, hora_inicio: "10:00", hora_fin: "12:00", observaciones: "Prueba" },
});
llamar("POST /reservas (cruce de horario -> error)", reservasCtrl, "crear", {
    body: { id_zona: 1, id_residencia: 102, fecha: FECHA_FUTURA, hora_inicio: "11:00", hora_fin: "13:00" },
});
llamar("PUT /reservas/1/estado (Confirmada)", reservasCtrl, "cambiarEstado", {
    params: { id: 1 }, body: { estado: "Confirmada" },
});
llamar("DELETE /reservas/1", reservasCtrl, "eliminar", { params: { id: 1 } });

console.log("\n========== MODULO: VIGILANTES ==========");
llamar("GET /vigilantes", vigilantesCtrl, "listar", { query: {} });
llamar("POST /vigilantes (nuevo vigilante)", vigilantesCtrl, "crear", {
    body: { nombre: "Marta Lopez", documento: "1099887766", telefono: "3005556677", turno: "Mixto" },
});

console.log("\n========== MODULO: VISITANTES ==========");
llamar("POST /visitantes (ingreso valido)", visitantesCtrl, "registrarIngreso", {
    body: { nombre: "Pedro Gomez", documento: "555666777", id_residencia: 105, id_vigilante: 1, motivo: "Entrega domicilio" },
});
llamar("POST /visitantes (mismo documento sin salida -> error)", visitantesCtrl, "registrarIngreso", {
    body: { nombre: "Pedro Gomez", documento: "555666777", id_residencia: 105, id_vigilante: 1 },
});
llamar("PUT /visitantes/1/salida", visitantesCtrl, "registrarSalida", { params: { id: 1 } });

console.log("\n========== MODULO: AUTENTICACION ==========");
llamar("POST /auth/registro", authCtrl, "registrar", {
    body: { nombre: "Laura Martinez", correo: "laura@horisoft.com", password: "clave123", rol: "Residente" },
});
llamar("POST /auth/login (correcto)", authCtrl, "login", {
    body: { correo: "laura@horisoft.com", password: "clave123" },
});
llamar("POST /auth/login (password incorrecto -> error)", authCtrl, "login", {
    body: { correo: "laura@horisoft.com", password: "incorrecta" },
});

console.log("\n========== MODULO: PQR ==========");
llamar("POST /pqr (crear queja)", pqrCtrl, "crear", {
    body: { id_residencia: 103, tipo: "Queja", asunto: "Mascota suelta", descripcion: "Perro sin correa en zona comun" },
});
llamar("PUT /pqr/1/respuesta", pqrCtrl, "responder", {
    params: { id: 1 }, body: { respuesta: "Se envio circular recordando el reglamento de mascotas" },
});
llamar("PUT /pqr/1/respuesta (ya cerrada -> error)", pqrCtrl, "responder", {
    params: { id: 1 }, body: { respuesta: "otra respuesta" },
});

console.log("\n========== MODULO: COMUNICACIONES ==========");
llamar("POST /comunicados", comunicadosCtrl, "crear", {
    body: { titulo: "Asamblea general", contenido: "Se cita a asamblea el 30 de agosto", dirigido_a: "Residentes", id_autor: 1 },
});
llamar("PUT /comunicados/2/archivar", comunicadosCtrl, "archivar", { params: { id: 2 } });

console.log("\n========== MODULO: FINANCIERA ==========");
llamar("GET /cuentas-cobro", cuentasCtrl, "listar", { query: {} });
llamar("POST /pagos (pago parcial)", pagosCtrl, "registrar", {
    body: { id_cuenta: 2, valor_pagado: 100000, metodo_pago: "Transferencia" },
});
llamar("POST /pagos (excede saldo -> error)", pagosCtrl, "registrar", {
    body: { id_cuenta: 2, valor_pagado: 100000, metodo_pago: "Transferencia" },
});
llamar("POST /pagos (completa el saldo)", pagosCtrl, "registrar", {
    body: { id_cuenta: 2, valor_pagado: 50000, metodo_pago: "Efectivo" },
});

console.log("\n========== MODULO: PROVEEDORES ==========");
llamar("POST /proveedores", proveedoresCtrl, "crear", {
    body: { nombre: "Seguridad Total SAS", nit: "900555444-2", servicio: "Vigilancia", telefono: "3201112233" },
});
llamar("DELETE /proveedores/1", proveedoresCtrl, "eliminar", { params: { id: 1 } });

console.log("\n========== MODULO: INVENTARIO ==========");
llamar("POST /inventario", inventarioCtrl, "crear", {
    body: { nombre: "Extintores", categoria: "Seguridad", cantidad: 10, ubicacion: "Pasillos" },
});
llamar("PUT /inventario/1/cantidad", inventarioCtrl, "actualizarCantidad", {
    params: { id: 1 }, body: { cantidad: 48 },
});

console.log("\n========== MODULO: VEHICULOS ==========");
llamar("POST /vehiculos", vehiculosCtrl, "crear", {
    body: { placa: "JKL456", id_residencia: 104, tipo: "Moto", color: "Rojo" },
});
llamar("POST /vehiculos (placa duplicada -> error)", vehiculosCtrl, "crear", {
    body: { placa: "ABC123", id_residencia: 106, tipo: "Carro" },
});

console.log("\n========== MODULO: DOCUMENTOS ==========");
llamar("POST /documentos", documentosCtrl, "crear", {
    body: { titulo: "Acta Asamblea 2026", tipo: "Acta", id_responsable: 1, url_archivo: "/docs/acta2026.pdf" },
});

console.log("\n========== MODULO: CONFIGURACION ==========");
llamar("PUT /configuracion/dia_pago_cuota", configuracionCtrl, "actualizarValor", {
    params: { clave: "dia_pago_cuota" }, body: { valor: "10" },
});
llamar("GET /configuracion", configuracionCtrl, "listar", { query: {} });

console.log("========== FIN DE LAS PRUEBAS ==========");
