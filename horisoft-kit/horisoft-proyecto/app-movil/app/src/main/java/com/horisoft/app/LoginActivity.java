package com.horisoft.app;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.horisoft.app.api.ApiClient;
import com.horisoft.app.util.SessionManager;

import org.json.JSONException;
import org.json.JSONObject;

public class LoginActivity extends AppCompatActivity {

    private static final String TAG = "LoginActivity";

    private EditText etCorreo;
    private EditText etPassword;
    private Button btnIngresar;
    private ProgressBar progressLogin;
    private TextView tvError;

    private SessionManager sesion;

    // ---------- Ciclo de vida de la Activity ----------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d(TAG, "onCreate llamado");

        sesion = new SessionManager(this);

        // Si ya hay una sesión guardada, no se vuelve a pedir el login.
        // (Si el token venció, la primera petición protegida devolverá 401/403
        // y ActividadProtegida enviará de vuelta a esta pantalla.)
        if (sesion.haySesion()) {
            irAHome();
            return;
        }

        setContentView(R.layout.activity_login);

        etCorreo = findViewById(R.id.etCorreo);
        etPassword = findViewById(R.id.etPassword);
        btnIngresar = findViewById(R.id.btnIngresar);
        progressLogin = findViewById(R.id.progressLogin);
        tvError = findViewById(R.id.tvError);

        btnIngresar.setOnClickListener(this::onClickIngresar);
    }

    @Override
    protected void onStart() {
        super.onStart();
        Log.d(TAG, "onStart llamado — la pantalla de login es visible");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume llamado — el usuario ya puede escribir sus credenciales");
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.d(TAG, "onPause llamado");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.d(TAG, "onStop llamado");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy llamado");
    }

    // ---------- Lógica de login ----------

    private void onClickIngresar(View view) {
        String correo = etCorreo.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        ocultarError();

        if (TextUtils.isEmpty(correo) || TextUtils.isEmpty(password)) {
            mostrarError(getString(R.string.login_error_campos_vacios));
            return;
        }

        mostrarCargando(true);

        JSONObject cuerpo = new JSONObject();
        try {
            cuerpo.put("correo", correo);
            cuerpo.put("password", password);
        } catch (JSONException e) {
            mostrarCargando(false);
            mostrarError(getString(R.string.login_error_conexion));
            return;
        }

        ApiClient.post("/auth/login", cuerpo, null, new ApiClient.Callback() {
            @Override
            public void onRespuesta(int codigoHttp, String respuesta) {
                if (isFinishing() || isDestroyed()) return;
                mostrarCargando(false);

                if (codigoHttp == 200) {
                    procesarLoginExitoso(respuesta);
                } else {
                    String mensaje = ApiClient.mensajeDe(respuesta, "");
                    Log.d(TAG, "Login rechazado (" + codigoHttp + "): " + mensaje);
                    // Un usuario inactivo recibe un mensaje propio del backend;
                    // para cualquier otro rechazo se muestra el texto genérico.
                    String texto = mensaje.toLowerCase().contains("inactivo")
                            ? mensaje
                            : getString(R.string.login_error_credenciales);
                    mostrarError(texto);
                    Toast.makeText(LoginActivity.this, texto, Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onErrorConexion(String detalle) {
                if (isFinishing() || isDestroyed()) return;
                mostrarCargando(false);
                Log.e(TAG, "Error de conexión: " + detalle);
                String texto = getString(R.string.login_error_conexion);
                mostrarError(texto);
                Toast.makeText(LoginActivity.this, texto, Toast.LENGTH_LONG).show();
            }
        });
    }

    private void procesarLoginExitoso(String respuesta) {
        try {
            JSONObject json = new JSONObject(respuesta);
            // El backend entrega el token ya con el prefijo "Bearer ".
            String token = json.getString("token");
            JSONObject usuario = json.getJSONObject("usuario");

            String nombre = usuario.optString("nombre", "");
            String correo = usuario.optString("correo", "");
            String rol = usuario.optString("rol", "");
            int idResidencia = usuario.optInt("id_residencia", 0); // null -> 0

            Log.d(TAG, "Login exitoso. Rol detectado: " + rol);
            sesion.guardar(token, nombre, correo, rol, idResidencia);

            Toast.makeText(this, "¡Bienvenido, " + nombre + "!", Toast.LENGTH_SHORT).show();
            irAHome();
        } catch (JSONException e) {
            Log.e(TAG, "Respuesta de login con formato inesperado", e);
            mostrarError(getString(R.string.login_error_conexion));
        }
    }

    private void irAHome() {
        startActivity(new Intent(this, HomeActivity.class));
        finish();
    }

    private void mostrarCargando(boolean mostrar) {
        progressLogin.setVisibility(mostrar ? View.VISIBLE : View.GONE);
        btnIngresar.setEnabled(!mostrar);
    }

    private void mostrarError(String mensaje) {
        tvError.setText(mensaje);
        tvError.setVisibility(View.VISIBLE);
    }

    private void ocultarError() {
        tvError.setVisibility(View.GONE);
    }
}
