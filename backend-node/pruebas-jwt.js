/**
 * Pruebas end-to-end del módulo de Autenticación (JWT)
 * ------------------------------------------------------------------
 * Ejecuta este archivo con:  node pruebas-jwt.js
 *
 * A diferencia de pruebas-manuales.js (que llama a los controladores
 * directamente con req/res simulados), este script SÍ levanta el
 * servidor Express real en un puerto de prueba y hace peticiones HTTP
 * reales con fetch, porque el middleware de autenticación depende del
 * header "Authorization" completo (algo que un req/res simulado no
 * reproduce con fidelidad).
 * ------------------------------------------------------------------
 */

const app = require("./app");

const PUERTO_PRUEBAS = 4000;
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
        // ---------- CP-JWT-01: login con credenciales correctas ----------
        const respLogin = await fetch(`${base}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "admin@horisoft.com", password: "admin123" }),
        });
        const cuerpoLogin = await respLogin.json();
        verificar("CP-JWT-01: login correcto responde 200", respLogin.status === 200);
        verificar("CP-JWT-01: la respuesta incluye un token", typeof cuerpoLogin.token === "string" && cuerpoLogin.token.startsWith("Bearer "));

        const token = cuerpoLogin.token;

        // ---------- CP-JWT-02: login con password incorrecto ----------
        const respLoginMalo = await fetch(`${base}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "admin@horisoft.com", password: "clave_incorrecta" }),
        });
        verificar("CP-JWT-02: login con password incorrecto responde 401", respLoginMalo.status === 401);

        // ---------- CP-JWT-03: ruta protegida SIN token ----------
        const respSinToken = await fetch(`${base}/usuarios`);
        verificar("CP-JWT-03: /usuarios sin token responde 401", respSinToken.status === 401);

        // ---------- CP-JWT-04: ruta protegida con token INVÁLIDO ----------
        const respTokenInvalido = await fetch(`${base}/usuarios`, {
            headers: { Authorization: "Bearer un.token.invalido" },
        });
        verificar("CP-JWT-04: /usuarios con token inválido responde 403", respTokenInvalido.status === 403);

        // ---------- CP-JWT-05: ruta protegida con token VÁLIDO ----------
        const respTokenValido = await fetch(`${base}/usuarios`, {
            headers: { Authorization: token },
        });
        const cuerpoUsuarios = await respTokenValido.json();
        verificar("CP-JWT-05: /usuarios con token válido responde 200", respTokenValido.status === 200);
        verificar("CP-JWT-05: /usuarios devuelve la lista de usuarios", Array.isArray(cuerpoUsuarios) && cuerpoUsuarios.length > 0);
        verificar("CP-JWT-05: el password nunca se expone", cuerpoUsuarios.every(u => u.password === undefined));

        // ---------- CP-JWT-06: /auth/perfil con token válido ----------
        const respPerfil = await fetch(`${base}/auth/perfil`, {
            headers: { Authorization: token },
        });
        const cuerpoPerfil = await respPerfil.json();
        verificar("CP-JWT-06: /auth/perfil responde 200 con token válido", respPerfil.status === 200);
        verificar("CP-JWT-06: el payload decodificado incluye el rol", cuerpoPerfil.usuario?.rol === "Administrador");

        // ---------- CP-JWT-07: header sin el esquema "Bearer" ----------
        const respFormatoMalo = await fetch(`${base}/usuarios`, {
            headers: { Authorization: token.replace("Bearer ", "") },
        });
        verificar("CP-JWT-07: token sin el prefijo 'Bearer' responde 401", respFormatoMalo.status === 401);

    } finally {
        servidor.close();
    }

    console.log(`\n--------------------------------------------------`);
    console.log(`Resultado: ${aciertos} pruebas correctas, ${fallos} fallidas.`);
    process.exit(fallos > 0 ? 1 : 0);
}

ejecutarPruebas();
