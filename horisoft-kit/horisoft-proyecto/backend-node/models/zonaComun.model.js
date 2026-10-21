/**
 * Modelo: ZonaComun
 * Basado en la entidad "Zona Comun" del MER de Horisoft (GA4-220501095-AA1-EV01).
 * PK explícita alineada al MER: id_zona (equivalente a id_zona_comun).
 */
class ZonaComun {
    constructor(id_zona, nombre, descripcion, capacidad, costo_reserva = 0, estado = "Disponible") {
        this.id_zona = id_zona;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.capacidad = capacidad;
        this.costo_reserva = costo_reserva;
        // Estados posibles: Disponible | Mantenimiento | Inactiva
        this.estado = estado;
    }
}

module.exports = ZonaComun;
