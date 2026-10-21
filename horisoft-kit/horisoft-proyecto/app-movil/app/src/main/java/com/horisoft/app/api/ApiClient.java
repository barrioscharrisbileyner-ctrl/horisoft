package com.horisoft.app.api;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Cliente HTTP genérico para el backend Express de Horisoft.
 *
 * Reemplaza al ApiClient de la primera versión (que solo sabía hacer login):
 * ahora cualquier módulo puede llamar a get / post / put con la misma lógica
 * (hilo secundario, timeouts, header Authorization y retorno al hilo principal).
 *
 * Sigue sin usar librerías externas (HttpURLConnection + org.json).
 *
 * Contrato con el backend:
 *  - El login devuelve el token YA con el prefijo "Bearer " ("Bearer eyJ...").
 *    Se guarda tal cual y se envía en el header Authorization sin modificarlo.
 *  - Lectura (GET) pública; escritura (POST/PUT/DELETE) exige token.
 *  - Los errores llegan como { "mensaje": "..." } en español.
 */
public class ApiClient {

    private static final String TAG = "ApiClient";

    /**
     * IMPORTANTE:
     *  - EMULADOR de Android Studio: tu computador se ve como 10.0.2.2
     *    (NO como localhost).
     *  - CELULAR FÍSICO en la misma red WiFi: usa la IP real de tu computador,
     *    por ejemplo "http://192.168.1.15:3000" (la ves con "ipconfig").
     */
    public static final String BASE_URL = "http://10.0.2.2:3000";

    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    private static final Handler mainThread = new Handler(Looper.getMainLooper());

    /** Resultado de una petición, siempre entregado en el hilo principal. */
    public interface Callback {
        /** El servidor respondió (con cualquier código HTTP). */
        void onRespuesta(int codigoHttp, String cuerpo);

        /** No hubo respuesta: sin red, servidor apagado, timeout, etc. */
        void onErrorConexion(String detalle);
    }

    public static void get(String ruta, String token, Callback callback) {
        solicitar("GET", ruta, null, token, callback);
    }

    public static void post(String ruta, JSONObject cuerpo, String token, Callback callback) {
        solicitar("POST", ruta, cuerpo, token, callback);
    }

    public static void put(String ruta, JSONObject cuerpo, String token, Callback callback) {
        solicitar("PUT", ruta, cuerpo, token, callback);
    }

    /** Extrae el campo "mensaje" de una respuesta de error; si no hay, devuelve el texto por defecto. */
    public static String mensajeDe(String cuerpo, String porDefecto) {
        try {
            return new JSONObject(cuerpo).optString("mensaje", porDefecto);
        } catch (JSONException e) {
            return porDefecto;
        }
    }

    private static void solicitar(String metodo, String ruta, JSONObject cuerpo,
                                  String token, Callback callback) {
        executor.execute(() -> {
            HttpURLConnection conexion = null;
            try {
                URL url = new URL(BASE_URL + ruta);
                conexion = (HttpURLConnection) url.openConnection();
                conexion.setRequestMethod(metodo);
                conexion.setRequestProperty("Accept", "application/json");
                conexion.setConnectTimeout(8000);
                conexion.setReadTimeout(8000);

                if (token != null && !token.isEmpty()) {
                    conexion.setRequestProperty("Authorization", token);
                }

                if (cuerpo != null) {
                    conexion.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
                    conexion.setDoOutput(true);
                    try (OutputStream os = conexion.getOutputStream()) {
                        os.write(cuerpo.toString().getBytes(StandardCharsets.UTF_8));
                    }
                }

                final int codigo = conexion.getResponseCode();
                final String respuesta = leer(
                        codigo >= 200 && codigo < 300
                                ? conexion.getInputStream()
                                : conexion.getErrorStream());

                Log.d(TAG, metodo + " " + ruta + " -> " + codigo);
                mainThread.post(() -> callback.onRespuesta(codigo, respuesta));

            } catch (IOException e) {
                Log.e(TAG, "Error de conexión en " + metodo + " " + ruta, e);
                final String detalle = e.getMessage();
                mainThread.post(() -> callback.onErrorConexion(detalle));
            } finally {
                if (conexion != null) {
                    conexion.disconnect();
                }
            }
        });
    }

    private static String leer(InputStream entrada) throws IOException {
        if (entrada == null) return "";
        StringBuilder sb = new StringBuilder();
        try (BufferedReader lector = new BufferedReader(
                new InputStreamReader(entrada, StandardCharsets.UTF_8))) {
            String linea;
            while ((linea = lector.readLine()) != null) {
                sb.append(linea);
            }
        }
        return sb.toString();
    }
}
