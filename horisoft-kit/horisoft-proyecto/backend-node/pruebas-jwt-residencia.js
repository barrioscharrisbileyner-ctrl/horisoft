/**
 * Pruebas end-to-end: usuario ligado a una residencia (id_residencia)
 * ------------------------------------------------------------------
 * Ejecuta con:  node pruebas-jwt-residencia.js
 *
 * Verifica que:
 *  - El login devuelve id_residencia (Residente: 1, Administrador: null).
 *  - El token JWT incluye id_residencia.
 *  - Un Residente reserva SIEMPRE a nombre de su residencia, aunque el body
 *    intente indicar otra.
 *  - Un usuario sin residencia (Administrador) debe indicar id_residencia.
 * ------------------------------------------------------------------
 */

const app = require("./app");

const PUERTO_PRUEBAS = 4002;
let aciertos = 0;
let fallos = 0;

function verificar(descripcion, condicion) {
    if (condicion) { aciertos++; console.log(`✅ ${descripcion}`); }
    else { fallos++; console.log(`❌ ${descripcion}`); }
}

function fechaFutura(dias) {
    return new Date(Date.now() + dias * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
}

async function login(base, correo, password) {
    const r = await fetch(`${base}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correo, password }),
    });
    return r.json();
}

function decodificarPayload(tokenConBearer) {
    const jwt = tokenConBearer.replace("Bearer ", "");
    return JSON.parse(Buffer.from(jwt.split(".")[1], "base64url").toString("utf8"));
}

async function ejecutarPruebas() {
    const servidor = app.listen(PUERTO_PRUEBAS);
    const base = `http://localhost:${PUERTO_PRUEBAS}`;

    try {
        const juan = await login(base, "juan.perez@horisoft.com", "juan123");
        const admin = await login(base, "admin@horisoft.com", "admin123");

        verificar("CP-RES-01: login del Residente devuelve id_residencia = 1", juan.usuario && juan.usuario.id_residencia === 1);
        verificar("CP-RES-02: login del Administrador devuelve id_residencia = null", admin.usuario && admin.usuario.id_residencia === null);
        verificar("CP-RES-03: el token del Residente incluye id_residencia = 1", decodificarPayload(juan.token).id_residencia === 1);

        // Residente intenta reservar a nombre de OTRA residencia (99)
        const r1 = await fetch(`${base}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: juan.token },
            body: JSON.stringify({ id_zona: 1, id_residencia: 99, fecha: fechaFutura(10), hora_inicio: "09:00", hora_fin: "10:00" }),
        });
        const cuerpo1 = await r1.json();
        verificar("CP-RES-04: Residente crea reserva (201)", r1.status === 201);
        verificar("CP-RES-05: la reserva queda a nombre de SU residencia (1), no la del body (99)", cuerpo1.reserva && cuerpo1.reserva.id_residencia === 1);

        // Administrador sin residencia: sin id_residencia en el body -> 400
        const r2 = await fetch(`${base}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: admin.token },
            body: JSON.stringify({ id_zona: 1, fecha: fechaFutura(11), hora_inicio: "09:00", hora_fin: "10:00" }),
        });
        verificar("CP-RES-06: Administrador sin id_residencia en el body recibe 400", r2.status === 400);

        // Administrador indicando id_residencia: se respeta
        const r3 = await fetch(`${base}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: admin.token },
            body: JSON.stringify({ id_zona: 1, id_residencia: 5, fecha: fechaFutura(11), hora_inicio: "09:00", hora_fin: "10:00" }),
        });
        const cuerpo3 = await r3.json();
        verificar("CP-RES-07: Administrador con id_residencia en el body crea la reserva (201)", r3.status === 201 && cuerpo3.reserva.id_residencia === 5);

    } catch (error) {
        fallos++;
        console.log("❌ Error inesperado en las pruebas:", error.message);
    } finally {
        servidor.close();
        if (servidor.closeAllConnections) servidor.closeAllConnections();
        console.log(`\nResultado: ${aciertos} correctas, ${fallos} fallidas.`);
        // process.exit() se evita a propósito: en Windows, forzar la salida mientras Node cierra
    // el servidor provoca «Assertion failed ... src\win\async.c» (código -1073740791).
    process.exitCode = fallos === 0 ? 0 : 1;
    }
}

ejecutarPruebas();
