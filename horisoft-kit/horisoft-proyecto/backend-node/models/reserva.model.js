/**
 * Modelo: Reserva
 * Basado en la entidad "Reserva" del MER de Horisoft (GA4-220501095-AA1-EV01).
 * Relaciona una Zona Comun (id_zona) con una Residencia/Persona (id_residencia)
 * que hace uso de ella en una fecha y franja horaria determinada.
 */
class Reserva {
    constructor(id_reserva, id_zona, id_residencia, fecha, hora_inicio, hora_fin, observaciones = "") {
        this.id_reserva = id_reserva;
        this.id_zona = id_zona;
        this.id_residencia = id_residencia;
        this.fecha = fecha;               // formato "YYYY-MM-DD"
        this.hora_inicio = hora_inicio;    // formato "HH:mm"
        this.hora_fin = hora_fin;          // formato "HH:mm"
        this.observaciones = observaciones;
        // Estados posibles: Pendiente | Confirmada | Cancelada
        this.estado = "Pendiente";
    }
}

module.exports = Reserva;
