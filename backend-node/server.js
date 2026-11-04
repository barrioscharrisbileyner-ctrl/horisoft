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

const servidor = app.listen(PUERTO, () => {
    console.log(`HORISOFT escuchando en http://localhost:${PUERTO}`);
});

let apagando = false;

function apagarServidor(signal) {
    if (apagando) return;
    apagando = true;
    console.log(`Señal ${signal} recibida; cerrando servidor HTTP...`);

    servidor.close(error => {
        if (error) {
            console.error("No se pudo cerrar el servidor HTTP correctamente:", error);
            process.exitCode = 1;
            return;
        }
        console.log("Servidor HTTP cerrado correctamente.");
    });
}

servidor.on("error", error => {
    console.error("Error del servidor HTTP:", error);
    process.exitCode = 1;
});

process.on("SIGINT", () => apagarServidor("SIGINT"));
process.on("SIGTERM", () => apagarServidor("SIGTERM"));
