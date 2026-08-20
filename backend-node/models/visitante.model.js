/**
 * Modelo: Visitante
 * Basado en la entidad "Visitante" del MER de Horisoft.
 * Representa un registro de ingreso/salida de una persona externa al
 * conjunto, autorizado por un vigilante y dirigido a una residencia.
 */
class Visitante {
    constructor(id_visita, nombre, documento, id_residencia, id_vigilante, motivo, placa_vehiculo = null) {
        this.id_visita = id_visita;
        this.nombre = nombre;
        this.documento = documento;
        this.id_residencia = id_residencia;   // A quién visita
        this.id_vigilante = id_vigilante;     // Quién autoriza el ingreso
        this.motivo = motivo;
        this.placa_vehiculo = placa_vehiculo; // Opcional

        this.fecha = new Date().toISOString().split("T")[0];
        this.hora_ingreso = new Date().toISOString();
        this.hora_salida = null;

        // Estados posibles: En instalación | Finalizada
        this.estado = "En instalación";
    }
}

module.exports = Visitante;
