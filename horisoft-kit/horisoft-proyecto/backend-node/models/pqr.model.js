/**
 * Modelo: PQR (Petición, Queja, Reclamo o Sugerencia)
 * Basado en el requerimiento RQ02 de Horisoft.
 */
class Pqr {
    constructor(id_pqr, id_residencia, tipo, asunto, descripcion) {
        this.id_pqr = id_pqr;
        this.id_residencia = id_residencia;
        // Tipos posibles: Petición | Queja | Reclamo | Sugerencia
        this.tipo = tipo;
        this.asunto = asunto;
        this.descripcion = descripcion;
        this.respuesta = null;
        this.fecha_creacion = new Date().toISOString();
        // Estados posibles: Abierta | En proceso | Cerrada
        this.estado = "Abierta";
    }
}

module.exports = Pqr;
