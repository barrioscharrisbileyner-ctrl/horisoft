package com.horisoft.app;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

/**
 * Pantalla de inicio: muestra quién inició sesión y un menú que depende del rol.
 *
 *  - Zonas comunes: para todos los roles (la lectura es pública en el backend).
 *  - Mis reservas: solo para usuarios asociados a una residencia.
 *
 * Los módulos siguientes (PQR, Comunicados, Visitantes...) se irán agregando
 * como botones nuevos de este menú.
 */
public class HomeActivity extends ActividadProtegida {

    private static final String TAG = "HomeActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (isFinishing()) return;
        setContentView(R.layout.activity_home);
        Log.d(TAG, "onCreate llamado");

        TextView tvBienvenida = findViewById(R.id.tvBienvenida);
        TextView tvRol = findViewById(R.id.tvRol);
        Button btnZonas = findViewById(R.id.btnZonasComunes);
        Button btnMisReservas = findViewById(R.id.btnMisReservas);
        Button btnCerrarSesion = findViewById(R.id.btnCerrarSesion);

        tvBienvenida.setText(getString(R.string.home_bienvenida) + ", " + sesion.getNombre());
        tvRol.setText(getString(R.string.home_rol_prefijo) + sesion.getRol());

        btnZonas.setOnClickListener(v ->
                startActivity(new Intent(this, ZonasComunesActivity.class)));

        btnMisReservas.setVisibility(sesion.puedeReservar() ? View.VISIBLE : View.GONE);
        btnMisReservas.setOnClickListener(v ->
                startActivity(new Intent(this, MisReservasActivity.class)));

        btnCerrarSesion.setOnClickListener(v -> cerrarSesion());
    }

    private void cerrarSesion() {
        Log.d(TAG, "Cerrando sesión y limpiando el token guardado");
        sesion.cerrar();
        irAlLogin();
    }
}
