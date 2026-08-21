/**
 * Pruebas end-to-end: JWT aplicado a PQR
 * ------------------------------------------------------------------
 * Ejecuta este archivo con:  node pruebas-jwt-pqr.js
 * ------------------------------------------------------------------
 */

const app = require("./app");

const PUERTO_PRUEBAS = 4002;
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

    try {
        const respLogin = await fetch(`${base}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "admin@horisoft.com", password: "admin123" }),
        });
        const { token } = await respLogin.json();

        // ---------- Lectura pública ----------
        const respListar = await fetch(`${base}/pqr`);
        verificar("CP-PQR-01: GET /pqr sin token responde 200 (lectura pública)", respListar.status === 200);

        // ---------- Crear: protegido ----------
        const payloadPqr = {
            id_residencia: 1,
            tipo: "Queja",
            asunto: "Ruido en horario nocturno",
            descripcion: "Se reporta ruido excesivo despues de las 10pm en la torre 2.",
        };

        const respCrearSinToken = await fetch(`${base}/pqr`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payloadPqr),
        });
        verificar("CP-PQR-02: POST /pqr sin token responde 401", respCrearSinToken.status === 401);

        const respCrearConToken = await fetch(`${base}/pqr`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: token },
            body: JSON.stringify(payloadPqr),
        });
        const cuerpoCrear = await respCrearConToken.json();
        verificar("CP-PQR-03: POST /pqr con token válido responde 201", respCrearConToken.status === 201);

        const idPqrCreada = cuerpoCrear.pqr && cuerpoCrear.pqr.id_pqr;

        // ---------- Responder: protegido ----------
        const respResponderSinToken = await fetch(`${base}/pqr/${idPqrCreada}/respuesta`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ respuesta: "Se realizará seguimiento con el vigilante de turno." }),
        });
        verificar("CP-PQR-04: PUT /pqr/:id/respuesta sin token responde 401", respResponderSinToken.status === 401);

        const respResponderConToken = await fetch(`${base}/pqr/${idPqrCreada}/respuesta`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", Authorization: token },
            body: JSON.stringify({ respuesta: "Se realizará seguimiento con el vigilante de turno." }),
        });
        verificar("CP-PQR-05: PUT /pqr/:id/respuesta con token válido responde 200", respResponderConToken.status === 200);

        // ---------- Eliminar: protegido, token inválido ----------
        const respEliminarTokenInvalido = await fetch(`${base}/pqr/${idPqrCreada}`, {
            method: "DELETE",
            headers: { Authorization: "Bearer token.falso" },
        });
        verificar("CP-PQR-06: DELETE /pqr/:id con token inválido responde 403", respEliminarTokenInvalido.status === 403);

    } finally {
        servidor.close();
    }

    console.log(`\n--------------------------------------------------`);
    console.log(`Resultado: ${aciertos} pruebas correctas, ${fallos} fallidas.`);
    process.exit(fallos > 0 ? 1 : 0);
}

ejecutarPruebas();
