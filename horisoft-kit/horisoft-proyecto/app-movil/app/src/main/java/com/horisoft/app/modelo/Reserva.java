package com.horisoft.app.modelo;

import org.json.JSONException;
import org.json.JSONObject;

/** Reserva tal como la entrega GET /reservas. */
public class Reserva {

    public static final String ESTADO_CANCELADA = "Cancelada";

    public final int id;
    public final int idZona;
    public final int idResidencia;
    public final String fecha;        // "YYYY-MM-DD"
    public final String horaInicio;   // "HH:mm"
    public final String horaFin;      // "HH:mm"
    public final String observaciones;
    public final String estado;

    public Reserva(int id, int idZona, int idResidencia, String fecha,
                   String horaInicio, String horaFin, String observaciones, String estado) {
        this.id = id;
        this.idZona = idZona;
        this.idResidencia = idResidencia;
        this.fecha = fecha;
        this.horaInicio = horaInicio;
        this.horaFin = horaFin;
        this.observaciones = observaciones;
        this.estado = estado;
    }

    public static Reserva desdeJson(JSONObject json) throws JSONException {
        return new Reserva(
                json.getInt("id_reserva"),
                json.getInt("id_zona"),
                json.getInt("id_residencia"),
                json.optString("fecha", ""),
                json.optString("hora_inicio", ""),
                json.optString("hora_fin", ""),
                json.optString("observaciones", ""),
                json.optString("estado", ""));
    }

    public boolean estaCancelada() {
        return ESTADO_CANCELADA.equals(estado);
    }
}
