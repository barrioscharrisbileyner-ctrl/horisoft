package com.horisoft.app;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.horisoft.app.util.SessionManager;

/**
 * Clase base de toda pantalla que exige sesión iniciada.
 *
 * - Si no hay sesión guardada, manda al Login y cierra la pantalla.
 * - Centraliza qué hacer cuando el backend responde 401/403 (token vencido
 *   o inválido; el token dura 1 hora por defecto).
 *
 * Uso en una subclase:
 *     super.onCreate(savedInstanceState);
 *     if (isFinishing()) return;   // no había sesión: ya se envió al Login
 */
public abstract class ActividadProtegida extends AppCompatActivity {

    protected SessionManager sesion;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        sesion = new SessionManager(this);
        if (!sesion.haySesion()) {
            irAlLogin();
        }
    }

    /** false si la pantalla ya se cerró: evita tocar la UI desde un callback tardío. */
    protected boolean activa() {
        return !isFinishing() && !isDestroyed();
    }

    /**
     * Llamar con el código HTTP de cada respuesta. Si es 401/403 cierra la sesión,
     * avisa y vuelve al Login; devuelve true para que el llamador deje de procesar.
     */
    protected boolean manejarErrorDeSesion(int codigoHttp) {
        if (codigoHttp == 401 || codigoHttp == 403) {
            Toast.makeText(this, R.string.sesion_expirada, Toast.LENGTH_LONG).show();
            sesion.cerrar();
            irAlLogin();
            return true;
        }
        return false;
    }

    protected void irAlLogin() {
        Intent intent = new Intent(this, LoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}
