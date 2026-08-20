/**
 * server.js — Punto de entrada de HORISOFT.
 *
 * Responsabilidad única: arrancar el servidor HTTP a partir de la
 * aplicación Express ya configurada en app.js (middlewares, rutas,
 * manejo de errores). app.js NO sabe en qué puerto corre ni cómo se
 * inicia; ese conocimiento vive únicamente aquí.
 */
const app = require("./app");

const PUERTO = process.env.PORT || 3000;

app.listen(PUERTO, () => {
    console.log(`HORISOFT escuchando en http://localhost:${PUERTO}`);
});
