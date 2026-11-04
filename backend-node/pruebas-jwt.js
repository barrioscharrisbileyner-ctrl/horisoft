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

process.env.NODE_ENV = "test";
const app = require("./app");
const { spawnSync } = require("node:child_process");

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
        verificar("CP-JWT-01: el login no expone el hash de contraseña", cuerpoLogin.usuario?.passwordHash === undefined);

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

        const respHeadSinToken = await fetch(`${base}/usuarios`, { method: "HEAD" });
        verificar("CP-JWT-03A: HEAD /usuarios sin token también responde 401", respHeadSinToken.status === 401);

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
        verificar("CP-JWT-05: ningún usuario expone passwordHash", cuerpoUsuarios.every(u => u.passwordHash === undefined));

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

        const respRegistroSinToken = await fetch(`${base}/auth/registro`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre: "Cuenta de prueba", correo: "prueba@horisoft.com", password: "clave123", rol: "Residente" }),
        });
        verificar("CP-JWT-08: el registro sin token responde 401", respRegistroSinToken.status === 401);

        const respLoginResidente = await fetch(`${base}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo: "juan.perez@horisoft.com", password: "juan123" }),
        });
        const { token: tokenResidente } = await respLoginResidente.json();

        const respRegistroResidente = await fetch(`${base}/auth/registro`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: tokenResidente },
            body: JSON.stringify({ nombre: "Cuenta de prueba", correo: "prueba@horisoft.com", password: "clave123", rol: "Administrador" }),
        });
        verificar("CP-JWT-09: un residente no puede crear usuarios", respRegistroResidente.status === 403);

        const respUsuariosResidente = await fetch(`${base}/usuarios`, {
            headers: { Authorization: tokenResidente },
        });
        verificar("CP-JWT-10: un residente no puede consultar todos los usuarios", respUsuariosResidente.status === 403);

        const respRegistroAdmin = await fetch(`${base}/auth/registro`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: token },
            body: JSON.stringify({ nombre: "Cuenta de prueba", correo: "prueba@horisoft.com", password: "clave123", rol: "Residente" }),
        });
        const cuerpoRegistro = await respRegistroAdmin.json();
        verificar("CP-JWT-11: un administrador puede crear usuarios", respRegistroAdmin.status === 201);
        verificar("CP-JWT-11: el registro no devuelve contraseñas ni hashes", cuerpoRegistro.usuario?.password === undefined && cuerpoRegistro.usuario?.passwordHash === undefined);

        const pruebaSinAdmin = spawnSync(process.execPath, ["-e", "require('./data/usuarios')"], {
            cwd: __dirname,
            encoding: "utf8",
            env: { ...process.env, NODE_ENV: "production", HORISOFT_ADMIN_EMAIL: "", HORISOFT_ADMIN_PASSWORD: "" },
        });
        verificar("CP-JWT-12: producción rechaza iniciar sin credenciales de administrador", pruebaSinAdmin.status !== 0);

        const pruebaSinEntorno = spawnSync(process.execPath, ["-e", "require('./data/usuarios')"], {
            cwd: __dirname,
            encoding: "utf8",
            env: { ...process.env, NODE_ENV: "", HORISOFT_ADMIN_EMAIL: "", HORISOFT_ADMIN_PASSWORD: "" },
        });
        verificar("CP-JWT-12A: un entorno no definido tampoco carga usuarios demo", pruebaSinEntorno.status !== 0);

        const pruebaAdminProduccion = spawnSync(process.execPath, [
            "-e",
            "const [u] = require('./data/usuarios'); if (u.correo !== process.env.HORISOFT_ADMIN_EMAIL || !u.passwordHash.startsWith('$2')) process.exitCode = 1;",
        ], {
            cwd: __dirname,
            encoding: "utf8",
            env: {
                ...process.env,
                NODE_ENV: "production",
                HORISOFT_ADMIN_EMAIL: "admin-test@example.invalid",
                HORISOFT_ADMIN_PASSWORD: "temporary-test-password-2026",
            },
        });
        verificar("CP-JWT-13: producción crea el administrador configurado con password hasheado", pruebaAdminProduccion.status === 0);

    } finally {
        servidor.close();
        if (servidor.closeAllConnections) servidor.closeAllConnections();
    }

    console.log(`\n--------------------------------------------------`);
    console.log(`Resultado: ${aciertos} pruebas correctas, ${fallos} fallidas.`);
    // process.exit() se evita a propósito: en Windows, forzar la salida mientras Node cierra
    // el servidor provoca «Assertion failed ... src\win\async.c» (código -1073740791).
    process.exitCode = fallos > 0 ? 1 : 0;
}

ejecutarPruebas();
