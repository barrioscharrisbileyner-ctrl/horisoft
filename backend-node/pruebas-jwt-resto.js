/**
 * Pruebas end-to-end: JWT aplicado a los 9 módulos restantes
 * (Financiera: Cuentas de Cobro y Pagos; Comunicaciones; Gestión Documental;
 *  Seguridad: Vigilantes y Visitantes y Vehículos; Inventario; Proveedores;
 *  Configuración)
 * ------------------------------------------------------------------
 * Ejecuta este archivo con:  node pruebas-jwt-resto.js
 *
 * Mismo criterio en todos: lectura (GET) pública, escritura
 * (POST/PUT/DELETE) protegida con Token JWT.
 * ------------------------------------------------------------------
 */

const app = require("./app");

const PUERTO_PRUEBAS = 4003;
let aciertos = 0;
let fallos = 0;

function verificar(descripcion, condicion) {
    if (condicion) {
        aciertos++;
        console.log(`✅ ${descripcion}`);
    } else {
        fallos++;
        console.log(`❌ ${descripcion}`);
    }
}

async function ejecutarPruebas() {
    const servidor = app.listen(PUERTO_PRUEBAS);
    const base = `http://localhost:${PUERTO_PRUEBAS}`;

    const jsonHeaders = (tok) => ({
        "Content-Type": "application/json",
        ...(tok ? { Authorization: tok } : {}),
    });

    try {
        const respLogin = await fetch(`${base}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "admin@horisoft.com", password: "admin123" }),
        });
        const { token } = await respLogin.json();

        // ================= CUENTAS DE COBRO =================
        const respListarCuentas = await fetch(`${base}/cuentas-cobro`);
        verificar("CP-FIN-01: GET /cuentas-cobro sin token responde 200", respListarCuentas.status === 200);

        const respCrearCuentaSinToken = await fetch(`${base}/cuentas-cobro`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ id_residencia: 1, concepto: "Administración Agosto", valor: 150000, fecha_vencimiento: "2026-09-05" }),
        });
        verificar("CP-FIN-02: POST /cuentas-cobro sin token responde 401", respCrearCuentaSinToken.status === 401);

        const respCrearCuenta = await fetch(`${base}/cuentas-cobro`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ id_residencia: 1, concepto: "Administración Agosto", valor: 150000, fecha_vencimiento: "2026-09-05" }),
        });
        const cuentaCreada = await respCrearCuenta.json();
        verificar("CP-FIN-03: POST /cuentas-cobro con token válido responde 201", respCrearCuenta.status === 201);
        const idCuenta = cuentaCreada.id_cuenta || (cuentaCreada.cuenta && cuentaCreada.cuenta.id_cuenta);

        // ================= PAGOS =================
        const respPagoSinToken = await fetch(`${base}/pagos`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ id_cuenta: idCuenta, valor_pagado: 150000, metodo_pago: "PSE" }),
        });
        verificar("CP-FIN-04: POST /pagos sin token responde 401", respPagoSinToken.status === 401);

        const respPagoConToken = await fetch(`${base}/pagos`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ id_cuenta: idCuenta, valor_pagado: 150000, metodo_pago: "PSE" }),
        });
        verificar("CP-FIN-05: POST /pagos con token válido responde 201", respPagoConToken.status === 201);

        // ================= COMUNICADOS =================
        const respComunicadoSinToken = await fetch(`${base}/comunicados`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ titulo: "Mantenimiento piscina", contenido: "La piscina estará cerrada por mantenimiento.", dirigido_a: "Todos", id_autor: 1 }),
        });
        verificar("CP-COM-01: POST /comunicados sin token responde 401", respComunicadoSinToken.status === 401);

        const respComunicadoConToken = await fetch(`${base}/comunicados`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ titulo: "Mantenimiento piscina", contenido: "La piscina estará cerrada por mantenimiento.", dirigido_a: "Todos", id_autor: 1 }),
        });
        verificar("CP-COM-02: POST /comunicados con token válido responde 201", respComunicadoConToken.status === 201);

        // ================= DOCUMENTOS =================
        const respDocSinToken = await fetch(`${base}/documentos`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ titulo: "Reglamento interno", tipo: "Reglamento", id_responsable: 1, url_archivo: "https://horisoft.local/reglamento.pdf" }),
        });
        verificar("CP-DOC-01: POST /documentos sin token responde 401", respDocSinToken.status === 401);

        const respDocConToken = await fetch(`${base}/documentos`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ titulo: "Reglamento interno", tipo: "Reglamento", id_responsable: 1, url_archivo: "https://horisoft.local/reglamento.pdf" }),
        });
        verificar("CP-DOC-02: POST /documentos con token válido responde 201", respDocConToken.status === 201);

        // ================= VIGILANTES =================
        const respVigSinToken = await fetch(`${base}/vigilantes`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ nombre: "Andrés Pérez", documento: "1102345678", turno: "Diurno" }),
        });
        verificar("CP-SEG-01: POST /vigilantes sin token responde 401", respVigSinToken.status === 401);

        const respVigConToken = await fetch(`${base}/vigilantes`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ nombre: "Andrés Pérez", documento: "1102345678", turno: "Diurno" }),
        });
        verificar("CP-SEG-02: POST /vigilantes con token válido responde 201", respVigConToken.status === 201);

        // ================= VISITANTES =================
        const respVisSinToken = await fetch(`${base}/visitantes`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ nombre: "Pedro Gómez", documento: "99887766", id_residencia: 1, id_vigilante: 1, motivo: "Visita familiar" }),
        });
        verificar("CP-SEG-03: POST /visitantes sin token responde 401", respVisSinToken.status === 401);

        const respVisConToken = await fetch(`${base}/visitantes`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ nombre: "Pedro Gómez", documento: "99887766", id_residencia: 1, id_vigilante: 1, motivo: "Visita familiar" }),
        });
        verificar("CP-SEG-04: POST /visitantes con token válido responde 201", respVisConToken.status === 201);

        // ================= VEHÍCULOS =================
        const respVehSinToken = await fetch(`${base}/vehiculos`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ placa: "XYZ789", id_residencia: 1, tipo: "Carro", color: "Negro" }),
        });
        verificar("CP-SEG-05: POST /vehiculos sin token responde 401", respVehSinToken.status === 401);

        const respVehConToken = await fetch(`${base}/vehiculos`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ placa: "XYZ789", id_residencia: 1, tipo: "Carro", color: "Negro" }),
        });
        verificar("CP-SEG-06: POST /vehiculos con token válido responde 201", respVehConToken.status === 201);

        // ================= INVENTARIO =================
        const respInvSinToken = await fetch(`${base}/inventario`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ nombre: "Silla plástica", categoria: "Mobiliario", cantidad: 30, ubicacion: "Bodega" }),
        });
        verificar("CP-INV-01: POST /inventario sin token responde 401", respInvSinToken.status === 401);

        const respInvConToken = await fetch(`${base}/inventario`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ nombre: "Silla plástica", categoria: "Mobiliario", cantidad: 30, ubicacion: "Bodega" }),
        });
        verificar("CP-INV-02: POST /inventario con token válido responde 201", respInvConToken.status === 201);

        // ================= PROVEEDORES =================
        const respProvSinToken = await fetch(`${base}/proveedores`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ nombre: "Aseo Total SAS", nit: "901987654-2", servicio: "Aseo y limpieza" }),
        });
        verificar("CP-PROV-01: POST /proveedores sin token responde 401", respProvSinToken.status === 401);

        const respProvConToken = await fetch(`${base}/proveedores`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ nombre: "Aseo Total SAS", nit: "901987654-2", servicio: "Aseo y limpieza" }),
        });
        verificar("CP-PROV-02: POST /proveedores con token válido responde 201", respProvConToken.status === 201);

        // ================= CONFIGURACIÓN =================
        const respConfSinToken = await fetch(`${base}/configuracion`, {
            method: "POST", headers: jsonHeaders(),
            body: JSON.stringify({ clave: "hora_cierre_zonas", valor: "22:00", descripcion: "Hora límite de uso de zonas comunes" }),
        });
        verificar("CP-CFG-01: POST /configuracion sin token responde 401", respConfSinToken.status === 401);

        const respConfConToken = await fetch(`${base}/configuracion`, {
            method: "POST", headers: jsonHeaders(token),
            body: JSON.stringify({ clave: "hora_cierre_zonas", valor: "22:00", descripcion: "Hora límite de uso de zonas comunes" }),
        });
        verificar("CP-CFG-02: POST /configuracion con token válido responde 201", respConfConToken.status === 201);

        // ================= Lectura pública de todos (control) =================
        for (const ruta of ["/comunicados", "/documentos", "/vigilantes", "/visitantes", "/vehiculos", "/inventario", "/proveedores", "/configuracion"]) {
            const r = await fetch(`${base}${ruta}`);
            verificar(`CP-LEC-${ruta}: GET ${ruta} sin token responde 200 (lectura pública)`, r.status === 200);
        }

    } finally {
        servidor.close();
    }

    console.log(`\n--------------------------------------------------`);
    console.log(`Resultado: ${aciertos} pruebas correctas, ${fallos} fallidas.`);
    process.exit(fallos > 0 ? 1 : 0);
}

ejecutarPruebas();
