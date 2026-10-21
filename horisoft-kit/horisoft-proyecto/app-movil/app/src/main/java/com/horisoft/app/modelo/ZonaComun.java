package com.horisoft.app.modelo;

import org.json.JSONException;
import org.json.JSONObject;

/** Zona común tal como la entrega GET /zonas-comunes. */
public class ZonaComun {

    public static final String ESTADO_DISPONIBLE = "Disponible";

    public final int id;
    public final String nombre;
    public final String descripcion;
    public final int capacidad;
    public final int costoReserva;
    public final String estado;

    public ZonaComun(int id, String nombre, String descripcion,
                     int capacidad, int costoReserva, String estado) {
        this.id = id;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.capacidad = capacidad;
        this.costoReserva = costoReserva;
        this.estado = estado;
    }

    public static ZonaComun desdeJson(JSONObject json) throws JSONException {
        return new ZonaComun(
                json.getInt("id_zona"),
                json.optString("nombre", ""),
                json.optString("descripcion", ""),
                json.optInt("capacidad", 0),
                json.optInt("costo_reserva", 0),
                json.optString("estado", ""));
    }

    public boolean estaDisponible() {
        return ESTADO_DISPONIBLE.equals(estado);
    }
}
