const inventario = require("../data/inventario");
const ItemInventario = require("../models/itemInventario.model");

const ESTADOS_VALIDOS = ["Bueno", "Regular", "Malo", "Fuera de servicio"];

class InventarioService {

    obtenerTodos() {
        return inventario;
    }

    obtenerPorId(id_item) {
        const item = inventario.find(i => i.id_item === Number(id_item));

        if (!item) {
            throw new Error("Ítem de inventario no encontrado");
        }

        return item;
    }

    /**
     * Reglas de negocio:
     *  1. nombre, categoria y cantidad son obligatorios.
     *  2. cantidad no puede ser negativa.
     */
    crear(datos) {

        const { nombre, categoria, cantidad, ubicacion, estado } = datos;

        if (!nombre || !categoria || cantidad === undefined) {
            throw new Error("nombre, categoria y cantidad son obligatorios");
        }

        if (cantidad < 0) {
            throw new Error("La cantidad no puede ser negativa");
        }

        if (estado && !ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const nuevoItem = new ItemInventario(
            inventario.length > 0
                ? Math.max(...inventario.map(i => i.id_item)) + 1
                : 1,
            nombre,
            categoria,
            cantidad,
            ubicacion || "",
            estado || "Bueno"
        );

        inventario.push(nuevoItem);

        return nuevoItem;
    }

    actualizarCantidad(id_item, cantidad) {

        if (cantidad === undefined || cantidad < 0) {
            throw new Error("La cantidad debe ser un número mayor o igual a cero");
        }

        const item = this.obtenerPorId(id_item);
        item.cantidad = cantidad;

        return item;
    }

    actualizarEstado(id_item, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const item = this.obtenerPorId(id_item);
        item.estado = estado;

        return item;
    }

    eliminar(id_item) {

        const indice = inventario.findIndex(i => i.id_item === Number(id_item));

        if (indice === -1) {
            throw new Error("Ítem de inventario no encontrado");
        }

        inventario.splice(indice, 1);
    }
}

module.exports = new InventarioService();
