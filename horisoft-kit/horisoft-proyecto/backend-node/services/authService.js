const jwt = require("jsonwebtoken");
const usuarios = require("../data/usuarios");
const Usuario = require("../models/usuario.model");

const ROLES_VALIDOS = ["Administrador", "Residente", "Vigilante", "Administrativo", "Proveedor"];
const ESTADOS_VALIDOS = ["Activo", "Inactivo"];

const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || "1h";

if (!JWT_SECRET) {
    // Falla rápido y con un mensaje claro si alguien olvida configurar el .env,
    // en vez de dejar que jwt.sign() lance un error críptico más adelante.
    throw new Error(
        "Falta JWT_SECRET en las variables de entorno. Revisa el archivo .env."
    );
}

class AuthService {

    obtenerTodos() {
        // No exponer la contraseña al listar usuarios
        return usuarios.map(({ password, ...resto }) => resto);
    }

    obtenerPorId(id_usuario) {
        const usuario = usuarios.find(u => u.id_usuario === Number(id_usuario));

        if (!usuario) {
            throw new Error("Usuario no encontrado");
        }

        return usuario;
    }

    /**
     * Reglas de negocio para el registro:
     *  1. nombre, correo, password y rol son obligatorios.
     *  2. El rol debe ser uno de los roles válidos del sistema.
     *  3. El correo debe ser único.
     */
    registrar(datos) {

        const { nombre, correo, password, rol, id_residencia } = datos;

        if (!nombre || !correo || !password || !rol) {
            throw new Error("nombre, correo, password y rol son obligatorios");
        }

        if (!ROLES_VALIDOS.includes(rol)) {
            throw new Error(`Rol inválido. Use uno de: ${ROLES_VALIDOS.join(", ")}`);
        }

        const correoDuplicado = usuarios.some(
            u => u.correo.toLowerCase() === correo.toLowerCase()
        );

        if (correoDuplicado) {
            throw new Error("Ya existe un usuario registrado con ese correo");
        }

        const nuevoUsuario = new Usuario(
            usuarios.length > 0
                ? Math.max(...usuarios.map(u => u.id_usuario)) + 1
                : 1,
            nombre,
            correo,
            password,
            rol,
            "Activo",
            id_residencia ? Number(id_residencia) : null
        );

        usuarios.push(nuevoUsuario);

        const { password: _oculto, ...usuarioSinPassword } = nuevoUsuario;
        return usuarioSinPassword;
    }

    /**
     * Reglas de negocio para el login:
     *  1. correo y password son obligatorios.
     *  2. El usuario debe existir y el password debe coincidir.
     *  3. El usuario debe estar en estado "Activo".
     * Si todo es correcto, genera y devuelve un Token JWT junto con los
     * datos del usuario (sin password).
     */
    login(correo, password) {

        if (!correo || !password) {
            throw new Error("correo y password son obligatorios");
        }

        const usuario = usuarios.find(
            u => u.correo.toLowerCase() === correo.toLowerCase()
        );

        // Mensaje genérico a propósito: no revelar si el correo existe o no,
        // para no facilitar enumeración de cuentas.
        if (!usuario || usuario.password !== password) {
            throw new Error("Credenciales inválidas");
        }

        if (usuario.estado !== "Activo") {
            throw new Error("El usuario se encuentra inactivo");
        }

        const { password: _oculto, ...usuarioSinPassword } = usuario;
        const token = this.generarToken(usuario);

        return { usuario: usuarioSinPassword, token };
    }

    /**
     * Genera un Token JWT firmado con JWT_SECRET.
     * Payload mínimo necesario para identificar y autorizar al usuario en
     * las peticiones siguientes, sin incluir el password.
     */
    generarToken(usuario) {
        const payload = {
            id_usuario: usuario.id_usuario,
            correo: usuario.correo,
            rol: usuario.rol,
            id_residencia: usuario.id_residencia,
        };

        return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
    }

    actualizarRol(id_usuario, rol) {

        if (!ROLES_VALIDOS.includes(rol)) {
            throw new Error(`Rol inválido. Use uno de: ${ROLES_VALIDOS.join(", ")}`);
        }

        const usuario = this.obtenerPorId(id_usuario);
        usuario.rol = rol;

        const { password, ...usuarioSinPassword } = usuario;
        return usuarioSinPassword;
    }

    actualizarEstado(id_usuario, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const usuario = this.obtenerPorId(id_usuario);
        usuario.estado = estado;

        const { password, ...usuarioSinPassword } = usuario;
        return usuarioSinPassword;
    }

    eliminar(id_usuario) {

        const indice = usuarios.findIndex(u => u.id_usuario === Number(id_usuario));

        if (indice === -1) {
            throw new Error("Usuario no encontrado");
        }

        usuarios.splice(indice, 1);
    }
}

module.exports = new AuthService();
