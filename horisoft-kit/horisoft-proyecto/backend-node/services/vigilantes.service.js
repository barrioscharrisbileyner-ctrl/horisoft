const vigilantes = require("../data/vigilantes");
const Vigilante = require("../models/vigilante.model");

const ESTADOS_VALIDOS = ["Activo", "Inactivo"];
const TURNOS_VALIDOS = ["Diurno", "Nocturno", "Mixto"];

class VigilantesService {

    obtenerTodas() {
        return vigilantes;
    }

    obtenerPorId(id_vigilante) {
        const vigilante = vigilantes.find(
            v => v.id_vigilante === Number(id_vigilante)
        );

        if (!vigilante) {
            throw new Error("Vigilante no encontrado");
        }

        return vigilante;
    }

    crear(datos) {

        if (!datos.nombre || !datos.documento || !datos.turno) {
            throw new Error("nombre, documento y turno son obligatorios");
        }

        if (!TURNOS_VALIDOS.includes(datos.turno)) {
            throw new Error(`Turno inválido. Use uno de: ${TURNOS_VALIDOS.join(", ")}`);
        }

        const documentoDuplicado = vigilantes.some(
            v => v.documento === datos.documento
        );

        if (documentoDuplicado) {
            throw new Error("Ya existe un vigilante registrado con ese documento");
        }

        const nuevoVigilante = new Vigilante(
            vigilantes.length > 0
                ? Math.max(...vigilantes.map(v => v.id_vigilante)) + 1
                : 1,
            datos.nombre,
            datos.documento,
            datos.telefono || "",
            datos.turno,
            datos.estado || "Activo"
        );

        vigilantes.push(nuevoVigilante);

        return nuevoVigilante;
    }

    actualizarEstado(id_vigilante, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const vigilante = this.obtenerPorId(id_vigilante);
        vigilante.estado = estado;

        return vigilante;
    }

    eliminar(id_vigilante) {

        const indice = vigilantes.findIndex(
            v => v.id_vigilante === Number(id_vigilante)
        );

        if (indice === -1) {
            throw new Error("Vigilante no encontrado");
        }

        vigilantes.splice(indice, 1);
    }
}

module.exports = new VigilantesService();
