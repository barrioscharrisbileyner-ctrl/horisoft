package com.horisoft.app;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;

import com.horisoft.app.api.ApiClient;
import com.horisoft.app.modelo.Reserva;
import com.horisoft.app.modelo.ZonaComun;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Reservas de la residencia del usuario.
 *
 * El backend no filtra por residencia (GET /reservas es público y devuelve
 * todas), así que el filtro se hace aquí con el id_residencia de la sesión.
 * Para mostrar el nombre de la zona se consulta primero /zonas-comunes.
 * Cancelar usa PUT /reservas/:id/estado con { "estado": "Cancelada" }.
 */
public class MisReservasActivity extends ActividadProtegida {

    private LinearLayout contenedor;
    private ProgressBar progreso;
    private TextView tvEstado;
    private Button btnReintentar;

    private final Map<Integer, String> nombresZona = new HashMap<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (isFinishing()) return;
        setContentView(R.layout.activity_mis_reservas);

        contenedor = findViewById(R.id.contenedorReservas);
        progreso = findViewById(R.id.progresoReservas);
        tvEstado = findViewById(R.id.tvEstadoReservas);
        btnReintentar = findViewById(R.id.btnReintentarReservas);

        btnReintentar.setOnClickListener(v -> cargar());
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Se recarga al volver, así una reserva nueva aparece sin hacer nada.
        if (sesion != null && sesion.haySesion()) {
            cargar();
        }
    }

    private void cargar() {
        contenedor.removeAllViews();
        tvEstado.setVisibility(View.GONE);
        btnReintentar.setVisibility(View.GONE);
        progreso.setVisibility(View.VISIBLE);

        // Paso 1: nombres de las zonas
        ApiClient.get("/zonas-comunes", sesion.getToken(), new ApiClient.Callback() {
            @Override
            public void onRespuesta(int codigoHttp, String cuerpo) {
                if (!activa()) return;
                if (manejarErrorDeSesion(codigoHttp)) return;
                if (codigoHttp == 200) {
                    try {
                        JSONArray arreglo = new JSONArray(cuerpo);
                        nombresZona.clear();
                        for (int i = 0; i < arreglo.length(); i++) {
                            ZonaComun z = ZonaComun.desdeJson(arreglo.getJSONObject(i));
                            nombresZona.put(z.id, z.nombre);
                        }
                    } catch (JSONException e) {
                        // Si falla, se mostrará "Zona #id" en vez del nombre.
                    }
                }
                cargarReservas();
            }

            @Override
            public void onErrorConexion(String detalle) {
                if (!activa()) return;
                falloConexion();
            }
        });
    }

    // Paso 2: reservas de esta residencia
    private void cargarReservas() {
        ApiClient.get("/reservas", sesion.getToken(), new ApiClient.Callback() {
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
                    List<Reserva> propias = new ArrayList<>();
                    for (int i = 0; i < arreglo.length(); i++) {
                        Reserva r = Reserva.desdeJson(arreglo.getJSONObject(i));
                        if (r.idResidencia == sesion.getIdResidencia()) {
                            propias.add(r);
                        }
                    }
                    if (propias.isEmpty()) {
                        tvEstado.setText(R.string.reservas_vacio);
                        tvEstado.setVisibility(View.VISIBLE);
                        return;
                    }
                    // Más recientes primero
                    Collections.sort(propias, (a, b) ->
                            (b.fecha + b.horaInicio).compareTo(a.fecha + a.horaInicio));
                    for (Reserva r : propias) {
                        agregarTarjeta(r);
                    }
                } catch (JSONException e) {
                    mostrarError(getString(R.string.error_cargar));
                }
            }

            @Override
            public void onErrorConexion(String detalle) {
                if (!activa()) return;
                falloConexion();
            }
        });
    }

    private void agregarTarjeta(Reserva reserva) {
        View tarjeta = LayoutInflater.from(this)
                .inflate(R.layout.item_reserva, contenedor, false);

        String zona = nombresZona.containsKey(reserva.idZona)
                ? nombresZona.get(reserva.idZona)
                : getString(R.string.reserva_zona_generica, reserva.idZona);
        ((TextView) tarjeta.findViewById(R.id.tvReservaItemZona)).setText(zona);
        ((TextView) tarjeta.findViewById(R.id.tvReservaItemHorario)).setText(
                getString(R.string.reserva_horario, reserva.fecha, reserva.horaInicio, reserva.horaFin));

        TextView tvEstadoReserva = tarjeta.findViewById(R.id.tvReservaItemEstado);
        tvEstadoReserva.setText(reserva.estado);
        tvEstadoReserva.setTextColor(getColor(
                reserva.estaCancelada() ? R.color.horisoft_error : R.color.horisoft_ok));

        Button btnCancelar = tarjeta.findViewById(R.id.btnCancelarReserva);
        if (reserva.estaCancelada()) {
            btnCancelar.setVisibility(View.GONE);
        } else {
            btnCancelar.setOnClickListener(v -> confirmarCancelacion(reserva));
        }

        contenedor.addView(tarjeta);
    }

    private void confirmarCancelacion(Reserva reserva) {
        new AlertDialog.Builder(this)
                .setTitle(R.string.reserva_cancelar_titulo)
                .setMessage(R.string.reserva_cancelar_mensaje)
                .setPositiveButton(R.string.reserva_cancelar_si, (d, w) -> cancelar(reserva))
                .setNegativeButton(R.string.reserva_cancelar_no, null)
                .show();
    }

    private void cancelar(Reserva reserva) {
        JSONObject cuerpo = new JSONObject();
        try {
            cuerpo.put("estado", Reserva.ESTADO_CANCELADA);
        } catch (JSONException e) {
            return;
        }
        progreso.setVisibility(View.VISIBLE);
        ApiClient.put("/reservas/" + reserva.id + "/estado", cuerpo, sesion.getToken(),
                new ApiClient.Callback() {
                    @Override
                    public void onRespuesta(int codigoHttp, String respuesta) {
                        if (!activa()) return;
                        if (manejarErrorDeSesion(codigoHttp)) return;
                        if (codigoHttp == 200) {
                            Toast.makeText(MisReservasActivity.this,
                                    R.string.reserva_cancelada, Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(MisReservasActivity.this,
                                    ApiClient.mensajeDe(respuesta, getString(R.string.error_cargar)),
                                    Toast.LENGTH_LONG).show();
                        }
                        cargar();
                    }

                    @Override
                    public void onErrorConexion(String detalle) {
                        if (!activa()) return;
                        progreso.setVisibility(View.GONE);
                        Toast.makeText(MisReservasActivity.this,
                                R.string.login_error_conexion, Toast.LENGTH_LONG).show();
                    }
                });
    }

    private void falloConexion() {
        progreso.setVisibility(View.GONE);
        mostrarError(getString(R.string.login_error_conexion));
    }

    private void mostrarError(String mensaje) {
        tvEstado.setText(mensaje);
        tvEstado.setVisibility(View.VISIBLE);
        btnReintentar.setVisibility(View.VISIBLE);
    }
}
