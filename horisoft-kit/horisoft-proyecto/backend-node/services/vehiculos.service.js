const vehiculos = require("../data/vehiculos");
const Vehiculo = require("../models/vehiculo.model");

const TIPOS_VALIDOS = ["Carro", "Moto", "Bicicleta"];
const ESTADOS_VALIDOS = ["Activo", "Inactivo"];

class VehiculosService {

    obtenerTodos() {
        return vehiculos;
    }

    obtenerPorId(id_vehiculo) {
        const vehiculo = vehiculos.find(v => v.id_vehiculo === Number(id_vehiculo));

        if (!vehiculo) {
            throw new Error("Vehículo no encontrado");
        }

        return vehiculo;
    }

    obtenerPorResidencia(id_residencia) {
        return vehiculos.filter(v => v.id_residencia === Number(id_residencia));
    }

    /**
     * Reglas de negocio:
     *  1. placa, id_residencia y tipo son obligatorios.
     *  2. tipo debe ser uno de los tipos válidos.
     *  3. La placa debe ser única (no se permiten vehículos duplicados).
     */
    crear(datos) {

        const { placa, id_residencia, tipo, color } = datos;

        if (!placa || !id_residencia || !tipo) {
            throw new Error("placa, id_residencia y tipo son obligatorios");
        }

        if (!TIPOS_VALIDOS.includes(tipo)) {
            throw new Error(`Tipo inválido. Use uno de: ${TIPOS_VALIDOS.join(", ")}`);
        }

        const placaDuplicada = vehiculos.some(
            v => v.placa === placa.toUpperCase()
        );

        if (placaDuplicada) {
            throw new Error("Ya existe un vehículo registrado con esa placa");
        }

        const nuevoVehiculo = new Vehiculo(
            vehiculos.length > 0
                ? Math.max(...vehiculos.map(v => v.id_vehiculo)) + 1
                : 1,
            placa,
            Number(id_residencia),
            tipo,
            color || ""
        );

        vehiculos.push(nuevoVehiculo);

        return nuevoVehiculo;
    }

    actualizarEstado(id_vehiculo, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const vehiculo = this.obtenerPorId(id_vehiculo);
        vehiculo.estado = estado;

        return vehiculo;
    }

    eliminar(id_vehiculo) {

        const indice = vehiculos.findIndex(v => v.id_vehiculo === Number(id_vehiculo));

        if (indice === -1) {
            throw new Error("Vehículo no encontrado");
        }

        vehiculos.splice(indice, 1);
    }
}

module.exports = new VehiculosService();
