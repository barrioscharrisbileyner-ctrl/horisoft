const Vigilante = require("../models/vigilante.model");

// "Base de datos" en memoria, precargada con vigilantes de ejemplo
// para poder probar el módulo de Visitantes de inmediato.
const vigilantes = [
    new Vigilante(1, "Carlos Ramírez", "1094567890", "3001234567", "Diurno", "Activo"),
    new Vigilante(2, "Luis Torres", "1098765432", "3007654321", "Nocturno", "Inactivo"),
];

module.exports = vigilantes;
