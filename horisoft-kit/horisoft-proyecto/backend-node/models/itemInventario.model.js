/**
 * Modelo: ItemInventario
 * Basado en el módulo de Inventario de Horisoft (bienes del conjunto).
 */
class ItemInventario {
    constructor(id_item, nombre, categoria, cantidad, ubicacion, estado = "Bueno") {
        this.id_item = id_item;
        this.nombre = nombre;
        this.categoria = categoria; // Ej: Mobiliario, Herramientas, Electrodomésticos
        this.cantidad = cantidad;
        this.ubicacion = ubicacion;
        // Estados posibles: Bueno | Regular | Malo | Fuera de servicio
        this.estado = estado;
    }
}

module.exports = ItemInventario;
