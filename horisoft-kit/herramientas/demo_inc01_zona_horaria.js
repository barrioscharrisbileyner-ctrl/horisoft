/**
 * Demostración INC-01: reserva "para hoy" (fecha de Colombia) rechazada como
 * "fecha pasada" cuando en UTC ya es el día siguiente (después de las 7 p.m. en Bogotá).
 * Uso:  TZ=America/Bogota node demo_inc01_zona_horaria.js   (desde la carpeta del backend)
 */
process.env.TZ = process.env.TZ || "America/Bogota";
const reservasService = require("./services/reservas.service");

// "Hoy" para una persona en Colombia (UTC-5):
const ahora = new Date();
const hoyColombia = new Date(ahora.getTime() - 5 * 60 * 60 * 1000).toISOString().split("T")[0];
const hoyUTC = ahora.toISOString().split("T")[0];
console.log(`Hora UTC:        ${ahora.toISOString()}`);
console.log(`Hoy en Colombia: ${hoyColombia}   |   Hoy en UTC (lo que usaba el servidor): ${hoyUTC}`);

try {
    const r = reservasService.crear({
        id_zona: 1, id_residencia: 1, fecha: hoyColombia,
        hora_inicio: "22:00", hora_fin: "23:00", observaciones: "reserva para hoy",
    });
    console.log(`✅ RESERVA ACEPTADA (id ${r.id_reserva}) para ${hoyColombia}`);
} catch (e) {
    console.log(`❌ RESERVA RECHAZADA: ${e.message}`);
}
