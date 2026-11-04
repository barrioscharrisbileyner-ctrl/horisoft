const Usuario = require("../models/usuario.model");

if (!["development", "test"].includes(process.env.NODE_ENV)) {
    const nombreAdmin = process.env.HORISOFT_ADMIN_NAME || "Administrador principal";
    const correoAdmin = process.env.HORISOFT_ADMIN_EMAIL?.trim();
    const passwordAdmin = process.env.HORISOFT_ADMIN_PASSWORD;

    if (!correoAdmin || !passwordAdmin || passwordAdmin.length < 12) {
        throw new Error(
            "Fuera de desarrollo/pruebas configura HORISOFT_ADMIN_EMAIL y HORISOFT_ADMIN_PASSWORD (mínimo 12 caracteres)."
        );
    }

    module.exports = [
        new Usuario(1, nombreAdmin, correoAdmin, passwordAdmin, "Administrador"),
    ];
} else {
    // Usuarios de demostración disponibles únicamente fuera de producción.
    module.exports = [
        new Usuario(1, "Admin Principal", "admin@horisoft.com", "admin123", "Administrador"),
        new Usuario(2, "Juan Pérez", "juan.perez@horisoft.com", "juan123", "Residente", "Activo", 1),
        new Usuario(3, "Carlos Ramírez", "carlos.vigilante@horisoft.com", "carlos123", "Vigilante"),
    ];
}
