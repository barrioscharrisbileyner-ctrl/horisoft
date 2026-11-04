package com.horisoft.app.api;

import android.content.Context;
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
import java.util.Iterator;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import com.horisoft.app.util.SessionManager;

/**
 * Cliente HTTP genérico para la API Django de Horisoft.
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
     *  - EMULADOR de Android Studio: el computador se ve como 10.0.2.2.
     *  - CELULAR FÍSICO en la misma red WiFi: cambia el host por la IP local
     *    del computador y conserva el prefijo /api/v1.
     */
    public static final String BASE_URL = "http://10.0.2.2:8000/api/v1";

    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    private static final Handler mainThread = new Handler(Looper.getMainLooper());
    private static volatile SessionManager sessionManager;

    public static void initialize(Context context) {
        sessionManager = new SessionManager(context);
    }

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

    /** Extrae un mensaje del formato de error de DRF o devuelve el texto por defecto. */
    public static String mensajeDe(String cuerpo, String porDefecto) {
        try {
            JSONObject json = new JSONObject(cuerpo);
            String mensaje = json.optString("mensaje", "");
            if (!mensaje.isEmpty()) return mensaje;
            mensaje = json.optString("detail", "");
            if (!mensaje.isEmpty()) return mensaje;
            Iterator<String> keys = json.keys();
            if (keys.hasNext()) {
                Object detalle = json.opt(keys.next());
                if (detalle instanceof org.json.JSONArray) {
                    return ((org.json.JSONArray) detalle).optString(0, porDefecto);
                }
                if (detalle instanceof String) return (String) detalle;
            }
            return porDefecto;
        } catch (JSONException e) {
            return porDefecto;
        }
    }

    private static void solicitar(String metodo, String ruta, JSONObject cuerpo,
                                  String token, Callback callback) {
        executor.execute(() -> {
            try {
                String tokenActual = token;
                HttpResponse respuesta = ejecutar(metodo, ruta, cuerpo, tokenActual);
                if (respuesta.codigo == 401 && tokenActual != null && !tokenActual.isEmpty()) {
                    String access = refrescarToken();
                    if (access != null) {
                        tokenActual = "Bearer " + access;
                        respuesta = ejecutar(metodo, ruta, cuerpo, tokenActual);
                    }
                }
                Log.d(TAG, metodo + " " + ruta + " -> " + respuesta.codigo);
                final int codigo = respuesta.codigo;
                final String contenido = respuesta.cuerpo;
                mainThread.post(() -> callback.onRespuesta(codigo, contenido));
            } catch (IOException e) {
                Log.e(TAG, "Error de conexión en " + metodo + " " + ruta, e);
                final String detalle = e.getMessage();
                mainThread.post(() -> callback.onErrorConexion(detalle));
            }
        });
    }

    private static HttpResponse ejecutar(String metodo, String ruta, JSONObject cuerpo,
                                         String token) throws IOException {
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
            int codigo = conexion.getResponseCode();
            String contenido = leer(
                    codigo >= 200 && codigo < 300
                            ? conexion.getInputStream()
                            : conexion.getErrorStream());
            return new HttpResponse(codigo, contenido);
        } finally {
            if (conexion != null) conexion.disconnect();
        }
    }

    private static String refrescarToken() {
        SessionManager manager = sessionManager;
        if (manager == null || manager.getRefreshToken() == null) return null;
        try {
            JSONObject cuerpo = new JSONObject();
            cuerpo.put("refresh", manager.getRefreshToken());
            HttpResponse respuesta = ejecutar("POST", "/auth/refresh/", cuerpo, null);
            if (respuesta.codigo != 200) return null;
            JSONObject json = new JSONObject(respuesta.cuerpo);
            String access = json.optString("access", "");
            if (access.isEmpty()) return null;
            String refresh = json.optString("refresh", manager.getRefreshToken());
            manager.actualizarTokens(access, refresh);
            return access;
        } catch (IOException | JSONException e) {
            Log.e(TAG, "No fue posible renovar la sesión.", e);
            return null;
        }
    }

    private static final class HttpResponse {
        final int codigo;
        final String cuerpo;

        HttpResponse(int codigo, String cuerpo) {
            this.codigo = codigo;
            this.cuerpo = cuerpo;
        }
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
