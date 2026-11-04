const reservas = require("../data/reservas");
const Reserva = require("../models/reserva.model");
const zonasComunesService = require("./zonasComunes.service");

/**
 * Convierte "HH:mm" a minutos desde medianoche, para poder comparar
 * franjas horarias fácilmente.
 */
function horaAMinutos(hora) {
    const [h, m] = hora.split(":").map(Number);
    return h * 60 + m;
}

/**
 * Determina si dos franjas horarias [inicioA, finA) y [inicioB, finB)
 * se solapan.
 */
function seSuperponen(inicioA, finA, inicioB, finB) {
    return inicioA < finB && inicioB < finA;
}

class ReservasService {

    obtenerTodas() {
        return reservas;
    }

    obtenerPorId(id_reserva) {
        const reserva = reservas.find(r => r.id_reserva === Number(id_reserva));

        if (!reserva) {
            throw new Error("Reserva no encontrada");
        }

        return reserva;
    }

    obtenerPorZona(id_zona) {
        return reservas.filter(r => r.id_zona === Number(id_zona));
    }

    /**
     * Reglas de negocio (equivalentes a ResidenciaForm.clean() en Django):
     *  1. La zona común debe existir.
     *  2. La zona común debe estar "Disponible" (no en Mantenimiento/Inactiva).
     *  3. La fecha de la reserva no puede ser anterior a hoy.
     *  4. hora_fin debe ser posterior a hora_inicio.
     *  5. No puede existir otra reserva activa (Pendiente/Confirmada) para la
     *     misma zona, misma fecha, con horario que se solape.
     */
    crear(datos) {

        const { id_zona, id_residencia, fecha, hora_inicio, hora_fin, observaciones } = datos;

        if (!id_zona || !id_residencia || !fecha || !hora_inicio || !hora_fin) {
            throw new Error(
                "id_zona, id_residencia, fecha, hora_inicio y hora_fin son obligatorios"
            );
        }

        // Regla 1: la zona debe existir (lanza error si no existe)
        const zona = zonasComunesService.obtenerPorId(id_zona);

        // Regla 2: la zona debe estar disponible
        if (zona.estado !== "Disponible") {
            throw new Error(
                `La zona "${zona.nombre}" no está disponible actualmente (estado: ${zona.estado})`
            );
        }

        // Regla 3: la fecha no puede ser en el pasado
        // Fecha local (no UTC): en Colombia (UTC-5), después de las 7 p.m. la fecha UTC
        // ya es la de mañana y rechazaba reservas de "hoy" como si fueran pasadas.
        const ahora = new Date();
        const hoy = new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60000)
            .toISOString().split("T")[0];
        if (fecha < hoy) {
            throw new Error("No se pueden crear reservas en fechas pasadas");
        }

        // Regla 4: hora_fin debe ser mayor que hora_inicio
        const inicioMin = horaAMinutos(hora_inicio);
        const finMin = horaAMinutos(hora_fin);

        if (finMin <= inicioMin) {
            throw new Error("La hora_fin debe ser posterior a la hora_inicio");
        }

        // Regla 5: no se permite solapamiento de horario en la misma zona/fecha
        const cruce = reservas.some(r =>
            r.id_zona === Number(id_zona) &&
            r.fecha === fecha &&
            r.estado !== "Cancelada" &&
            seSuperponen(inicioMin, finMin, horaAMinutos(r.hora_inicio), horaAMinutos(r.hora_fin))
        );

        if (cruce) {
            throw new Error(
                "Ya existe una reserva activa para esa zona en ese horario"
            );
        }

        const nuevaReserva = new Reserva(
            reservas.length > 0
                ? Math.max(...reservas.map(r => r.id_reserva)) + 1
                : 1,
            Number(id_zona),
            Number(id_residencia),
            fecha,
            hora_inicio,
            hora_fin,
            observaciones
        );

        reservas.push(nuevaReserva);

        return nuevaReserva;
    }

    cambiarEstado(id_reserva, estado) {

        const ESTADOS_VALIDOS = ["Pendiente", "Confirmada", "Cancelada"];

        if (!ESTADOS_VALIDOS.includes(estado)) {
            throw new Error(
                `Estado inválido. Use uno de: ${ESTADOS_VALIDOS.join(", ")}`
            );
        }

        const reserva = this.obtenerPorId(id_reserva);
        reserva.estado = estado;

        return reserva;
    }

    eliminar(id_reserva) {

        const indice = reservas.findIndex(
            r => r.id_reserva === Number(id_reserva)
        );

        if (indice === -1) {
            throw new Error("Reserva no encontrada");
        }

        reservas.splice(indice, 1);
    }
}

module.exports = new ReservasService();
