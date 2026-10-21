const comunicados = require("../data/comunicados");
const Comunicado = require("../models/comunicado.model");

const DESTINATARIOS_VALIDOS = ["Todos", "Administradores", "Residentes", "Vigilantes"];

class ComunicadosService {

    obtenerTodos(soloPublicados = false) {
        if (soloPublicados) {
            return comunicados.filter(c => c.estado === "Publicado");
        }
        return comunicados;
    }

    obtenerPorId(id_comunicado) {
        const comunicado = comunicados.find(
            c => c.id_comunicado === Number(id_comunicado)
        );

        if (!comunicado) {
            throw new Error("Comunicado no encontrado");
        }

        return comunicado;
    }

    /**
     * Reglas de negocio:
     *  1. titulo, contenido, dirigido_a e id_autor son obligatorios.
     *  2. dirigido_a debe ser uno de los destinatarios válidos.
     */
    crear(datos) {

        const { titulo, contenido, dirigido_a, id_autor } = datos;

        if (!titulo || !contenido || !dirigido_a || !id_autor) {
            throw new Error("titulo, contenido, dirigido_a e id_autor son obligatorios");
        }

        if (!DESTINATARIOS_VALIDOS.includes(dirigido_a)) {
            throw new Error(`dirigido_a inválido. Use uno de: ${DESTINATARIOS_VALIDOS.join(", ")}`);
        }

        const nuevoComunicado = new Comunicado(
            comunicados.length > 0
                ? Math.max(...comunicados.map(c => c.id_comunicado)) + 1
                : 1,
            titulo,
            contenido,
            dirigido_a,
            Number(id_autor)
        );

        comunicados.push(nuevoComunicado);

        return nuevoComunicado;
    }

    archivar(id_comunicado) {

        const comunicado = this.obtenerPorId(id_comunicado);

        if (comunicado.estado === "Archivado") {
            throw new Error("El comunicado ya está archivado");
        }

        comunicado.estado = "Archivado";

        return comunicado;
    }

    eliminar(id_comunicado) {

        const indice = comunicados.findIndex(
            c => c.id_comunicado === Number(id_comunicado)
        );

        if (indice === -1) {
            throw new Error("Comunicado no encontrado");
        }

        comunicados.splice(indice, 1);
    }
}

module.exports = new ComunicadosService();
