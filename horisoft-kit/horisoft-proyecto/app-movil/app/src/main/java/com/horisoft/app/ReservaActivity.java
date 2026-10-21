package com.horisoft.app;

import android.app.DatePickerDialog;
import android.app.TimePickerDialog;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.horisoft.app.api.ApiClient;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Calendar;
import java.util.Locale;

/**
 * Formulario para reservar una zona común (POST /reservas, ruta protegida).
 *
 * La residencia NO se pide: el backend la toma del token del usuario
 * (por eso solo reservan los usuarios asociados a una residencia).
 * Las reglas de negocio (zona disponible, fecha no pasada, cruce de horario)
 * las valida el backend y su mensaje se muestra tal cual.
 */
public class ReservaActivity extends ActividadProtegida {

    public static final String EXTRA_ID_ZONA = "id_zona";
    public static final String EXTRA_NOMBRE_ZONA = "nombre_zona";

    private int idZona;

    private EditText etFecha;
    private EditText etHoraInicio;
    private EditText etHoraFin;
    private EditText etObservaciones;
    private Button btnConfirmar;
    private ProgressBar progreso;
    private TextView tvMensaje;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (isFinishing()) return;

        idZona = getIntent().getIntExtra(EXTRA_ID_ZONA, 0);
        if (idZona == 0 || !sesion.puedeReservar()) {
            Toast.makeText(this, R.string.zona_solo_residentes, Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        setContentView(R.layout.activity_reserva);

        ((TextView) findViewById(R.id.tvReservaZona))
                .setText(getIntent().getStringExtra(EXTRA_NOMBRE_ZONA));

        etFecha = findViewById(R.id.etFecha);
        etHoraInicio = findViewById(R.id.etHoraInicio);
        etHoraFin = findViewById(R.id.etHoraFin);
        etObservaciones = findViewById(R.id.etObservaciones);
        btnConfirmar = findViewById(R.id.btnConfirmarReserva);
        progreso = findViewById(R.id.progresoReserva);
        tvMensaje = findViewById(R.id.tvMensajeReserva);

        etFecha.setOnClickListener(v -> elegirFecha());
        etHoraInicio.setOnClickListener(v -> elegirHora(etHoraInicio, 8));
        etHoraFin.setOnClickListener(v -> elegirHora(etHoraFin, 10));
        btnConfirmar.setOnClickListener(v -> confirmar());
    }

    private void elegirFecha() {
        Calendar hoy = Calendar.getInstance();
        DatePickerDialog dialogo = new DatePickerDialog(this,
                (vista, anio, mes, dia) -> etFecha.setText(
                        String.format(Locale.US, "%04d-%02d-%02d", anio, mes + 1, dia)),
                hoy.get(Calendar.YEAR), hoy.get(Calendar.MONTH), hoy.get(Calendar.DAY_OF_MONTH));
        dialogo.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
        dialogo.show();
    }

    private void elegirHora(EditText campo, int horaInicial) {
        new TimePickerDialog(this,
                (vista, hora, minuto) -> campo.setText(
                        String.format(Locale.US, "%02d:%02d", hora, minuto)),
                horaInicial, 0, true).show();
    }

    private void confirmar() {
        tvMensaje.setVisibility(View.GONE);

        String fecha = etFecha.getText().toString().trim();
        String horaInicio = etHoraInicio.getText().toString().trim();
        String horaFin = etHoraFin.getText().toString().trim();
        String observaciones = etObservaciones.getText().toString().trim();

        if (TextUtils.isEmpty(fecha) || TextUtils.isEmpty(horaInicio) || TextUtils.isEmpty(horaFin)) {
            mostrarMensaje(getString(R.string.reserva_error_campos), true);
            return;
        }
        // "HH:mm" con ceros a la izquierda se compara bien como texto.
        if (horaFin.compareTo(horaInicio) <= 0) {
            mostrarMensaje(getString(R.string.reserva_error_horas), true);
            return;
        }

        JSONObject cuerpo = new JSONObject();
        try {
            cuerpo.put("id_zona", idZona);
            cuerpo.put("fecha", fecha);
            cuerpo.put("hora_inicio", horaInicio);
            cuerpo.put("hora_fin", horaFin);
            cuerpo.put("observaciones", observaciones);
        } catch (JSONException e) {
            mostrarMensaje(getString(R.string.error_cargar), true);
            return;
        }

        cargando(true);
        ApiClient.post("/reservas", cuerpo, sesion.getToken(), new ApiClient.Callback() {
            @Override
            public void onRespuesta(int codigoHttp, String respuesta) {
                if (!activa()) return;
                cargando(false);
                if (manejarErrorDeSesion(codigoHttp)) return;

                if (codigoHttp == 201) {
                    Toast.makeText(ReservaActivity.this,
                            R.string.reserva_creada, Toast.LENGTH_LONG).show();
                    finish();
                } else {
                    // Mensajes del backend: zona en mantenimiento, cruce de horario, etc.
                    mostrarMensaje(ApiClient.mensajeDe(respuesta,
                            getString(R.string.error_cargar)), true);
                }
            }

            @Override
            public void onErrorConexion(String detalle) {
                if (!activa()) return;
                cargando(false);
                mostrarMensaje(getString(R.string.login_error_conexion), true);
            }
        });
    }

    private void cargando(boolean mostrar) {
        progreso.setVisibility(mostrar ? View.VISIBLE : View.GONE);
        btnConfirmar.setEnabled(!mostrar);
    }

    private void mostrarMensaje(String texto, boolean esError) {
        tvMensaje.setText(texto);
        tvMensaje.setTextColor(getColor(esError ? R.color.horisoft_error : R.color.horisoft_ok));
        tvMensaje.setVisibility(View.VISIBLE);
    }
}
