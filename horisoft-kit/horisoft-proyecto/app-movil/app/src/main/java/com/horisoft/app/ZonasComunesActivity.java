package com.horisoft.app;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.horisoft.app.api.ApiClient;
import com.horisoft.app.modelo.ZonaComun;

import org.json.JSONArray;
import org.json.JSONException;

import java.text.NumberFormat;
import java.util.Locale;

/**
 * Lista las zonas comunes (GET /zonas-comunes, lectura pública) y permite
 * reservar las que estén "Disponible".
 */
public class ZonasComunesActivity extends ActividadProtegida {

    private LinearLayout contenedor;
    private ProgressBar progreso;
    private TextView tvEstado;
    private Button btnReintentar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (isFinishing()) return;
        setContentView(R.layout.activity_zonas_comunes);

        contenedor = findViewById(R.id.contenedorZonas);
        progreso = findViewById(R.id.progresoZonas);
        tvEstado = findViewById(R.id.tvEstadoZonas);
        btnReintentar = findViewById(R.id.btnReintentarZonas);

        btnReintentar.setOnClickListener(v -> cargarZonas());
        cargarZonas();
    }

    private void cargarZonas() {
        contenedor.removeAllViews();
        tvEstado.setVisibility(View.GONE);
        btnReintentar.setVisibility(View.GONE);
        progreso.setVisibility(View.VISIBLE);

        ApiClient.get("/zonas-comunes", sesion.getToken(), new ApiClient.Callback() {
            @Override
            public void onRespuesta(int codigoHttp, String cuerpo) {
                if (!activa()) return;
                progreso.setVisibility(View.GONE);
                if (manejarErrorDeSesion(codigoHttp)) return;

                if (codigoHttp != 200) {
                    mostrarError(ApiClient.mensajeDe(cuerpo, getString(R.string.error_cargar)));
                    return;
                }
                try {
                    JSONArray arreglo = new JSONArray(cuerpo);
                    if (arreglo.length() == 0) {
                        mostrarError(getString(R.string.zonas_vacio));
                        btnReintentar.setVisibility(View.GONE);
                        return;
                    }
                    for (int i = 0; i < arreglo.length(); i++) {
                        agregarTarjeta(ZonaComun.desdeJson(arreglo.getJSONObject(i)));
                    }
                } catch (JSONException e) {
                    mostrarError(getString(R.string.error_cargar));
                }
            }

            @Override
            public void onErrorConexion(String detalle) {
                if (!activa()) return;
                progreso.setVisibility(View.GONE);
                mostrarError(getString(R.string.login_error_conexion));
            }
        });
    }

    private void agregarTarjeta(ZonaComun zona) {
        View tarjeta = LayoutInflater.from(this)
                .inflate(R.layout.item_zona_comun, contenedor, false);

        ((TextView) tarjeta.findViewById(R.id.tvZonaNombre)).setText(zona.nombre);
        ((TextView) tarjeta.findViewById(R.id.tvZonaDescripcion)).setText(zona.descripcion);

        String costo = zona.costoReserva > 0
                ? getString(R.string.zona_costo,
                        NumberFormat.getIntegerInstance(new Locale("es", "CO")).format(zona.costoReserva))
                : getString(R.string.zona_sin_costo);
        ((TextView) tarjeta.findViewById(R.id.tvZonaDetalle))
                .setText(getString(R.string.zona_capacidad, zona.capacidad) + "  ·  " + costo);

        TextView tvEstadoZona = tarjeta.findViewById(R.id.tvZonaEstado);
        tvEstadoZona.setText(zona.estado);
        tvEstadoZona.setTextColor(getColor(
                zona.estaDisponible() ? R.color.horisoft_ok : R.color.horisoft_aviso));

        Button btnReservar = tarjeta.findViewById(R.id.btnReservar);
        boolean puede = zona.estaDisponible() && sesion.puedeReservar();
        btnReservar.setEnabled(puede);
        btnReservar.setAlpha(puede ? 1f : 0.5f);
        if (!zona.estaDisponible()) {
            btnReservar.setText(R.string.zona_no_disponible);
        } else if (!sesion.puedeReservar()) {
            btnReservar.setText(R.string.zona_solo_residentes);
        }
        btnReservar.setOnClickListener(v -> {
            Intent intent = new Intent(this, ReservaActivity.class);
            intent.putExtra(ReservaActivity.EXTRA_ID_ZONA, zona.id);
            intent.putExtra(ReservaActivity.EXTRA_NOMBRE_ZONA, zona.nombre);
            startActivity(intent);
        });

        contenedor.addView(tarjeta);
    }

    private void mostrarError(String mensaje) {
        tvEstado.setText(mensaje);
        tvEstado.setVisibility(View.VISIBLE);
        btnReintentar.setVisibility(View.VISIBLE);
    }
}
