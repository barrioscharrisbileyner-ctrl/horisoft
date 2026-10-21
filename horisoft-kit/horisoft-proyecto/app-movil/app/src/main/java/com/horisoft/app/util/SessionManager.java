package com.horisoft.app.util;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Guarda y entrega los datos de la sesión del usuario autenticado.
 * Usa el mismo archivo de preferencias de la primera versión ("horisoft_prefs").
 */
public class SessionManager {

    private static final String PREFS = "horisoft_prefs";
    private static final String K_TOKEN = "token";
    private static final String K_NOMBRE = "nombre";
    private static final String K_CORREO = "correo";
    private static final String K_ROL = "rol";
    private static final String K_ID_RESIDENCIA = "id_residencia";

    public static final String ROL_RESIDENTE = "Residente";

    private final SharedPreferences prefs;

    public SessionManager(Context contexto) {
        this.prefs = contexto.getApplicationContext()
                .getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    /** idResidencia = 0 cuando el usuario no está asociado a una residencia. */
    public void guardar(String token, String nombre, String correo, String rol, int idResidencia) {
        prefs.edit()
                .putString(K_TOKEN, token)
                .putString(K_NOMBRE, nombre)
                .putString(K_CORREO, correo)
                .putString(K_ROL, rol)
                .putInt(K_ID_RESIDENCIA, idResidencia)
                .apply();
    }

    public void cerrar() {
        prefs.edit().clear().apply();
    }

    public boolean haySesion() {
        String token = getToken();
        return token != null && !token.isEmpty();
    }

    /** Token tal como lo entrega el backend, con el prefijo "Bearer ". */
    public String getToken() { return prefs.getString(K_TOKEN, null); }

    public String getNombre() { return prefs.getString(K_NOMBRE, ""); }

    public String getCorreo() { return prefs.getString(K_CORREO, ""); }

    public String getRol() { return prefs.getString(K_ROL, ""); }

    public int getIdResidencia() { return prefs.getInt(K_ID_RESIDENCIA, 0); }

    public boolean esResidente() { return ROL_RESIDENTE.equals(getRol()); }

    /** Puede crear reservas quien pertenece a una residencia (el backend usa la del token). */
    public boolean puedeReservar() { return getIdResidencia() > 0; }
}
