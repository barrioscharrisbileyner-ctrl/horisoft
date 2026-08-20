/**
 * Modelo: Documento
 * Basado en el requerimiento RQ06 (Gestión Documental) de Horisoft.
 */
class Documento {
    constructor(id_documento, titulo, tipo, id_responsable, url_archivo) {
        this.id_documento = id_documento;
        this.titulo = titulo;
        // Tipos posibles: Reglamento | Acta | Circular | Otro
        this.tipo = tipo;
        this.id_responsable = id_responsable; // Quién lo subió
        this.url_archivo = url_archivo;
        this.fecha_subida = new Date().toISOString();
    }
}

module.exports = Documento;
