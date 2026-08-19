const ItemInventario = require("../models/itemInventario.model");

const inventario = [
    new ItemInventario(1, "Sillas plásticas", "Mobiliario", 50, "Depósito Salón Social", "Bueno"),
    new ItemInventario(2, "Guadaña", "Herramientas", 1, "Depósito de mantenimiento", "Regular"),
];

module.exports = inventario;
