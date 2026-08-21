/**
 * Pruebas end-to-end: JWT aplicado a Zonas Comunes y Reservas
 * ------------------------------------------------------------------
 * Ejecuta este archivo con:  node pruebas-jwt-modulos.js
 *
 * Verifica que:
 *  - La lectura (GET) de zonas comunes y reservas sigue siendo pública.
 *  - La escritura (POST/PUT/DELETE) exige un Token JWT válido.
 * ------------------------------------------------------------------
 */

const app = require("./app");

const PUERTO_PRUEBAS = 4001;
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
        // Token válido, reutilizado en varias pruebas
        const respLogin = await fetch(`${base}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "admin@horisoft.com", password: "admin123" }),
        });
        const { token } = await respLogin.json();

        // ---------- Zonas Comunes: lectura pública ----------
        const respListarZonas = await fetch(`${base}/zonas-comunes`);
        verificar("CP-MOD-01: GET /zonas-comunes sin token responde 200 (lectura pública)", respListarZonas.status === 200);

        // ---------- Zonas Comunes: escritura protegida ----------
        const respCrearZonaSinToken = await fetch(`${base}/zonas-comunes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre: "Gimnasio", descripcion: "Zona de ejercicio", capacidad: 15, costo_reserva: 0 }),
        });
        verificar("CP-MOD-02: POST /zonas-comunes sin token responde 401", respCrearZonaSinToken.status === 401);

        const respCrearZonaConToken = await fetch(`${base}/zonas-comunes`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: token },
            body: JSON.stringify({ nombre: "Gimnasio", descripcion: "Zona de ejercicio", capacidad: 15, costo_reserva: 0 }),
        });
        verificar("CP-MOD-03: POST /zonas-comunes con token válido responde 201", respCrearZonaConToken.status === 201);

        // ---------- Reservas: lectura pública ----------
        const respListarReservas = await fetch(`${base}/reservas`);
        verificar("CP-MOD-04: GET /reservas sin token responde 200 (lectura pública)", respListarReservas.status === 200);

        // ---------- Reservas: escritura protegida ----------
        const payloadReserva = {
            id_zona: 2,
            id_residencia: 1,
            fecha: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0], // 7 días adelante, siempre futura
            hora_inicio: "10:00",
            hora_fin: "11:00",
        };

        const respCrearReservaSinToken = await fetch(`${base}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payloadReserva),
        });
        verificar("CP-MOD-05: POST /reservas sin token responde 401", respCrearReservaSinToken.status === 401);

        const respCrearReservaConToken = await fetch(`${base}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: token },
            body: JSON.stringify(payloadReserva),
        });
        verificar("CP-MOD-06: POST /reservas con token válido responde 201", respCrearReservaConToken.status === 201);

        const respCrearReservaTokenInvalido = await fetch(`${base}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: "Bearer token.falso" },
            body: JSON.stringify(payloadReserva),
        });
        verificar("CP-MOD-07: POST /reservas con token inválido responde 403", respCrearReservaTokenInvalido.status === 403);

    } finally {
        servidor.close();
    }

    console.log(`\n--------------------------------------------------`);
    console.log(`Resultado: ${aciertos} pruebas correctas, ${fallos} fallidas.`);
    process.exit(fallos > 0 ? 1 : 0);
}

ejecutarPruebas();
