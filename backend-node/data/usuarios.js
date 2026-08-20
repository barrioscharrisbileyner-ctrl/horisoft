const Usuario = require("../models/usuario.model");

// "Base de datos" en memoria, con un usuario de cada rol para poder probar.
const usuarios = [
    new Usuario(1, "Admin Principal", "admin@horisoft.com", "admin123", "Administrador"),
    new Usuario(2, "Juan Pérez", "juan.perez@horisoft.com", "juan123", "Residente"),
    new Usuario(3, "Carlos Ramírez", "carlos.vigilante@horisoft.com", "carlos123", "Vigilante"),
];

module.exports = usuarios;
