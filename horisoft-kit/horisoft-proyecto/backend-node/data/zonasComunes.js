const ZonaComun = require("../models/zonaComun.model");

// "Base de datos" en memoria. Se precarga con zonas comunes típicas
// de un conjunto residencial para poder probar el módulo de Reservas.
const zonasComunes = [
    new ZonaComun(1, "Salón Social", "Salón para eventos y reuniones", 50, 80000, "Disponible"),
    new ZonaComun(2, "Piscina", "Piscina para adultos y niños", 30, 0, "Disponible"),
    new ZonaComun(3, "Cancha Múltiple", "Cancha de fútbol/baloncesto", 20, 30000, "Mantenimiento"),
];

module.exports = zonasComunes;
