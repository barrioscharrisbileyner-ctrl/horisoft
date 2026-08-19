const proveedores = require("../data/proveedores");
const Proveedor = require("../models/proveedor.model");

const ESTADOS_VALIDOS = ["Activo", "Inactivo"];

class ProveedoresService {

    obtenerTodos() {
        return proveedores;
    }

    obtenerPorId(id_proveedor) {
        const proveedor = proveedores.find(
            p => p.id_proveedor === Number(id_proveedor)
        );

        if (!proveedor) {
            throw new Error("Proveedor no encontrado");
        }

        return proveedor;
    }

    /**
     * Reglas de negocio:
     *  1. nombre, nit y servicio son obligatorios.
     *  2. El NIT debe ser único.
     */
    crear(datos) {

        const { nombre, nit, servicio, telefono } = datos;

        if (!nombre || !nit || !servicio) {
            throw new Error("nombre, nit y servicio son obligatorios");
        }

        const nitDuplicado = proveedores.some(p => p.nit === nit);

        if (nitDuplicado) {
            throw new Error("Ya existe un proveedor registrado con ese NIT");
        }

        const nuevoProveedor = new Proveedor(
            proveedores.length > 0
                ? Math.max(...proveedores.map(p => p.id_proveedor)) + 1
                : 1,
            nombre,
            nit,
            servicio,
            telefono || ""
        );

        proveedores.push(nuevoProveedor);

        return nuevoProveedor;
    }

    actualizarEstado(id_proveedor, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const proveedor = this.obtenerPorId(id_proveedor);
        proveedor.estado = estado;

        return proveedor;
    }

    eliminar(id_proveedor) {

        const indice = proveedores.findIndex(
            p => p.id_proveedor === Number(id_proveedor)
        );

        if (indice === -1) {
            throw new Error("Proveedor no encontrado");
        }

        proveedores.splice(indice, 1);
    }
}

module.exports = new ProveedoresService();
