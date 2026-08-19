const zonasComunes = require("../data/zonasComunes");
const ZonaComun = require("../models/zonaComun.model");

const ESTADOS_VALIDOS = ["Disponible", "Mantenimiento", "Inactiva"];

class ZonasComunesService {

    obtenerTodas() {
        return zonasComunes;
    }

    obtenerPorId(id_zona) {
        const zona = zonasComunes.find(z => z.id_zona === Number(id_zona));

        if (!zona) {
            throw new Error("Zona común no encontrada");
        }

        return zona;
    }

    crear(datos) {

        if (!datos.nombre || !datos.capacidad) {
            throw new Error("nombre y capacidad son obligatorios");
        }

        const nuevaZona = new ZonaComun(
            zonasComunes.length > 0
                ? Math.max(...zonasComunes.map(z => z.id_zona)) + 1
                : 1,
            datos.nombre,
            datos.descripcion || "",
            datos.capacidad,
            datos.costo_reserva || 0,
            datos.estado || "Disponible"
        );

        zonasComunes.push(nuevaZona);

        return nuevaZona;
    }

    actualizarEstado(id_zona, estado) {

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(
                `Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`
            );
        }

        const zona = this.obtenerPorId(id_zona);
        zona.estado = estado;

        return zona;
    }

    eliminar(id_zona) {

        const indice = zonasComunes.findIndex(
            z => z.id_zona === Number(id_zona)
        );

        if (indice === -1) {
            throw new Error("Zona común no encontrada");
        }

        zonasComunes.splice(indice, 1);
    }
}

module.exports = new ZonasComunesService();
