const Comunicado = require("../models/comunicado.model");

const comunicados = [
    new Comunicado(1, "Mantenimiento de piscina", "La piscina estará cerrada por mantenimiento el próximo lunes.", "Todos", 1),
];

module.exports = comunicados;
