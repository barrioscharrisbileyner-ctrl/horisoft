const visitantes = require("../data/visitantes");
const Visitante = require("../models/visitante.model");
const vigilantesService = require("./vigilantes.service");

class VisitantesService {

    obtenerTodas() {
        return visitantes;
    }

    obtenerPorId(id_visita) {
        const visita = visitantes.find(v => v.id_visita === Number(id_visita));

        if (!visita) {
            throw new Error("Registro de visita no encontrado");
        }

        return visita;
    }

    obtenerActivas() {
        return visitantes.filter(v => v.estado === "En instalación");
    }

    /**
     * Reglas de negocio para el registro de ingreso (equivalentes al
     * clean() de ResidenciaForm en el módulo Django):
     *  1. nombre, documento, id_residencia e id_vigilante son obligatorios.
     *  2. El vigilante debe existir y estar en estado "Activo".
     *  3. Un mismo documento no puede tener más de un ingreso activo
     *     simultáneo (sin salida registrada).
     */
    registrarIngreso(datos) {

        const { nombre, documento, id_residencia, id_vigilante, motivo, placa_vehiculo } = datos;

        if (!nombre || !documento || !id_residencia || !id_vigilante) {
            throw new Error(
                "nombre, documento, id_residencia e id_vigilante son obligatorios"
            );
        }

        // Regla 2: el vigilante debe existir y estar activo
        const vigilante = vigilantesService.obtenerPorId(id_vigilante);

        if (vigilante.estado !== "Activo") {
            throw new Error(
                `El vigilante "${vigilante.nombre}" no está activo en este turno`
            );
        }

        // Regla 3: no permitir doble ingreso activo con el mismo documento
        const yaEstaAdentro = visitantes.some(
            v => v.documento === documento && v.estado === "En instalación"
        );

        if (yaEstaAdentro) {
            throw new Error(
                "Este visitante ya tiene un ingreso activo sin salida registrada"
            );
        }

        const nuevaVisita = new Visitante(
            visitantes.length > 0
                ? Math.max(...visitantes.map(v => v.id_visita)) + 1
                : 1,
            nombre,
            documento,
            Number(id_residencia),
            Number(id_vigilante),
            motivo || "",
            placa_vehiculo || null
        );

        visitantes.push(nuevaVisita);

        return nuevaVisita;
    }

    /**
     * Registra la salida de un visitante.
     * Regla: solo se puede registrar salida si la visita existe y su
     * estado actual es "En instalación" (no se puede cerrar dos veces).
     */
    registrarSalida(id_visita) {

        const visita = this.obtenerPorId(id_visita);

        if (visita.estado !== "En instalación") {
            throw new Error("Esta visita ya tiene una salida registrada");
        }

        visita.hora_salida = new Date().toISOString();
        visita.estado = "Finalizada";

        return visita;
    }

    eliminar(id_visita) {

        const indice = visitantes.findIndex(
            v => v.id_visita === Number(id_visita)
        );

        if (indice === -1) {
            throw new Error("Registro de visita no encontrado");
        }

        visitantes.splice(indice, 1);
    }
}

module.exports = new VisitantesService();
