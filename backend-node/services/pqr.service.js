const pqrs = require("../data/pqrs");
const Pqr = require("../models/pqr.model");

const TIPOS_VALIDOS = ["Petición", "Queja", "Reclamo", "Sugerencia"];
const ESTADOS_VALIDOS = ["Abierta", "En proceso", "Cerrada"];

class PqrService {

    obtenerTodas() {
        return pqrs;
    }

    obtenerPorId(id_pqr) {
        const pqr = pqrs.find(p => p.id_pqr === Number(id_pqr));

        if (!pqr) {
            throw new Error("PQR no encontrada");
        }

        return pqr;
    }

    obtenerPorResidencia(id_residencia) {
        return pqrs.filter(p => p.id_residencia === Number(id_residencia));
    }

    /**
     * Reglas de negocio:
     *  1. id_residencia, tipo, asunto y descripcion son obligatorios.
     *  2. El tipo debe ser uno de los tipos válidos.
     */
    crear(datos) {

        const { id_residencia, tipo, asunto, descripcion } = datos;

        if (!id_residencia || !tipo || !asunto || !descripcion) {
            throw new Error("id_residencia, tipo, asunto y descripcion son obligatorios");
        }

        if (!TIPOS_VALIDOS.includes(tipo)) {
            throw new Error(`Tipo inválido. Use uno de: ${TIPOS_VALIDOS.join(", ")}`);
        }

        const nuevaPqr = new Pqr(
            pqrs.length > 0 ? Math.max(...pqrs.map(p => p.id_pqr)) + 1 : 1,
            Number(id_residencia),
            tipo,
            asunto,
            descripcion
        );

        pqrs.push(nuevaPqr);

        return nuevaPqr;
    }

    /**
     * Reglas de negocio para responder:
     *  1. La PQR debe existir.
     *  2. No se puede responder una PQR que ya está "Cerrada".
     *  3. Al responder, la PQR pasa automáticamente a estado "Cerrada".
     */
    responder(id_pqr, respuesta) {

        if (!respuesta) {
            throw new Error("La respuesta no puede estar vacía");
        }

        const pqr = this.obtenerPorId(id_pqr);

        if (pqr.estado === "Cerrada") {
            throw new Error("No se puede responder una PQR que ya está cerrada");
        }

        pqr.respuesta = respuesta;
        pqr.estado = "Cerrada";

        return pqr;
    }

    cambiarEstado(id_pqr, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(`Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`);
        }

        const pqr = this.obtenerPorId(id_pqr);
        pqr.estado = estado;

        return pqr;
    }

    eliminar(id_pqr) {

        const indice = pqrs.findIndex(p => p.id_pqr === Number(id_pqr));

        if (indice === -1) {
            throw new Error("PQR no encontrada");
        }

        pqrs.splice(indice, 1);
    }
}

module.exports = new PqrService();
