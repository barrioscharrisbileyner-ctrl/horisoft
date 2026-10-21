/**
 * Demostración INC-04 (contraseñas sin cifrar) e INC-05 (sin control de roles):
 *  - INC-05: un usuario con rol Residente crea una zona común (acción de administración).
 *  - INC-04: las contraseñas se guardan en texto plano en la capa de datos.
 * Uso:  node demo_inc04_inc05_seguridad.js   (desde la carpeta del backend)
 */
const app = require("./app");
const usuarios = require("./data/usuarios");

(async () => {
    const servidor = app.listen(4010);
    const base = "http://localhost:4010";
    try {
        const login = await (await fetch(`${base}/auth/login`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "juan.perez@horisoft.com", password: "juan123" }),
        })).json();
        console.log(`Usuario autenticado: ${login.usuario.nombre} | rol: ${login.usuario.rol}`);

        const r = await fetch(`${base}/zonas-comunes`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: login.token },
            body: JSON.stringify({ nombre: "Zona creada por un Residente", capacidad: 10 }),
        });
        console.log(`INC-05  POST /zonas-comunes con rol Residente -> HTTP ${r.status} ` +
            (r.status === 201 ? "❌ (debería ser 403: solo Administrador/Administrativo)" : "✅"));

        const p = usuarios.find(u => u.rol === "Residente");
        const enClaro = typeof p.password === "string" && !/^\$2[aby]\$|^pbkdf2|^[a-f0-9]{64}$/.test(p.password);
        console.log(`INC-04  contraseña almacenada del Residente: "${p.password}" ` +
            (enClaro ? "❌ (texto plano, sin hash)" : "✅ (con hash)"));
    } finally { servidor.close(); }
})();
