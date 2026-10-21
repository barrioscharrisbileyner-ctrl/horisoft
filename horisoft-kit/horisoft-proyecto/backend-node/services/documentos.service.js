const documentos = require("../data/documentos");
const Documento = require("../models/documento.model");

const TIPOS_VALIDOS = ["Reglamento", "Acta", "Circular", "Otro"];

class DocumentosService {

    obtenerTodos() {
        return documentos;
    }

    obtenerPorId(id_documento) {
        const documento = documentos.find(
            d => d.id_documento === Number(id_documento)
        );

        if (!documento) {
            throw new Error("Documento no encontrado");
        }

        return documento;
    }

    obtenerPorTipo(tipo) {
        return documentos.filter(d => d.tipo === tipo);
    }

    /**
     * Reglas de negocio:
     *  1. titulo, tipo, id_responsable y url_archivo son obligatorios.
     *  2. tipo debe ser uno de los tipos válidos.
     */
    crear(datos) {

        const { titulo, tipo, id_responsable, url_archivo } = datos;

        if (!titulo || !tipo || !id_responsable || !url_archivo) {
            throw new Error("titulo, tipo, id_responsable y url_archivo son obligatorios");
        }

        if (!TIPOS_VALIDOS.includes(tipo)) {
            throw new Error(`Tipo inválido. Use uno de: ${TIPOS_VALIDOS.join(", ")}`);
        }

        const nuevoDocumento = new Documento(
            documentos.length > 0
                ? Math.max(...documentos.map(d => d.id_documento)) + 1
                : 1,
            titulo,
            tipo,
            Number(id_responsable),
            url_archivo
        );

        documentos.push(nuevoDocumento);

        return nuevoDocumento;
    }

    eliminar(id_documento) {

        const indice = documentos.findIndex(
            d => d.id_documento === Number(id_documento)
        );

        if (indice === -1) {
            throw new Error("Documento no encontrado");
        }

        documentos.splice(indice, 1);
    }
}

module.exports = new DocumentosService();
