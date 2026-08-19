/**
 * Modelo: Vigilante
 * Basado en la entidad "Vigilante" del MER de Horisoft (rol de Seguridad).
 */
class Vigilante {
    constructor(id_vigilante, nombre, documento, telefono, turno, estado = "Activo") {
        this.id_vigilante = id_vigilante;
        this.nombre = nombre;
        this.documento = documento;
        this.telefono = telefono;
        // Turnos posibles: Diurno | Nocturno | Mixto
        this.turno = turno;
        // Estados posibles: Activo | Inactivo
        this.estado = estado;
    }
}

module.exports = Vigilante;
