/**
 * Modelo: Comunicado
 * Basado en el requerimiento RQ04 (Comunicaciones) de Horisoft.
 */
class Comunicado {
    constructor(id_comunicado, titulo, contenido, dirigido_a, id_autor) {
        this.id_comunicado = id_comunicado;
        this.titulo = titulo;
        this.contenido = contenido;
        // Valores posibles: Todos | Administradores | Residentes | Vigilantes
        this.dirigido_a = dirigido_a;
        this.id_autor = id_autor;
        this.fecha_publicacion = new Date().toISOString();
        // Estados posibles: Publicado | Archivado
        this.estado = "Publicado";
    }
}

module.exports = Comunicado;
