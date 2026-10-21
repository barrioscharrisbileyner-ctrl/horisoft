# Horisoft — App móvil Android

App Android (Java + XML, sin librerías externas) que consume el backend Express
con JWT de Horisoft. Paquete: `com.horisoft.app`.

## Qué incluye hoy

| Módulo | Pantallas | Endpoints |
|---|---|---|
| Autenticación | Login (con sesión persistente) y Home por rol | `POST /auth/login` |
| Zonas Comunes y Reservas (RQ03) | Zonas comunes, Nueva reserva, Mis reservas (con cancelar) | `GET /zonas-comunes`, `GET/POST /reservas`, `PUT /reservas/:id/estado` |

## Cómo ejecutarla

1. **Backend:** en `backend-node/` aplica el contenido de `backend-patch/`, crea el
   `.env` a partir de `.env.example` y ejecuta `npm install` y `npm run dev`
   (puerto 3000 por defecto).
2. **App:** abre la carpeta `app-movil/` en Android Studio, espera el *Gradle Sync*
   y ejecuta en un emulador (probado en Pixel 5, API 30).
3. **URL del servidor:** `ApiClient.BASE_URL = "http://10.0.2.2:3000"` sirve para el
   emulador. Con un celular físico cámbiala por la IP de tu computador en la red
   (por ejemplo `http://192.168.1.15:3000`).

Usuarios de prueba del backend:

| Rol | Correo | Contraseña | Residencia |
|---|---|---|---|
| Administrador | admin@horisoft.com | admin123 | — |
| Residente | juan.perez@horisoft.com | juan123 | 1 |
| Vigilante | carlos.vigilante@horisoft.com | carlos123 | — |

## Estructura

```
app/src/main/java/com/horisoft/app/
├── LoginActivity.java          login + auto-login si ya hay sesión
├── HomeActivity.java           menú según el rol
├── ZonasComunesActivity.java   lista de zonas
├── ReservaActivity.java        formulario de reserva
├── MisReservasActivity.java    reservas de la residencia + cancelar
├── ActividadProtegida.java     base: exige sesión y maneja 401/403
├── api/ApiClient.java          cliente HTTP genérico (get/post/put)
├── modelo/                     ZonaComun, Reserva
└── util/SessionManager.java    token y datos de sesión
```

Cómo agregar un módulo nuevo: crear su Activity extendiendo `ActividadProtegida`,
llamar a `ApiClient.get/post/put(...)` con `sesion.getToken()`, llamar a
`manejarErrorDeSesion(codigo)` en cada respuesta y añadir un botón en `HomeActivity`.

## Decisiones de diseño

- El token se guarda **tal como lo entrega el backend** (`"Bearer eyJ..."`) y se envía
  sin modificarlo en el header `Authorization`.
- La residencia **no se pide** en el formulario: el backend la toma del token.
- Los mensajes de las reglas de negocio (cruce de horario, zona en mantenimiento,
  fecha pasada) los valida el backend y la app los muestra tal cual.
- Lectura pública / escritura protegida, igual que en el backend.

## Plan de pruebas manuales (emulador) — para capturas de evidencia

| Caso | Pasos | Resultado esperado |
|---|---|---|
| CP-MOV-01 | Login con Juan Pérez | Home con "Rol: Residente" y botón "Mis reservas" |
| CP-MOV-02 | Login con admin | Home sin botón "Mis reservas" |
| CP-MOV-03 | Contraseña incorrecta | "Correo o contraseña incorrectos" |
| CP-MOV-04 | Campos vacíos | "Ingresa tu correo y tu contraseña" |
| CP-MOV-05 | Backend apagado e intentar login | Mensaje de falta de conexión |
| CP-MOV-06 | Iniciar sesión, cerrar la app y abrirla | Entra directo al Home |
| CP-MOV-07 | Abrir "Zonas comunes" | 3 zonas; la Cancha aparece "No disponible" |
| CP-MOV-08 | Juan reserva la Piscina, fecha futura | "Reserva creada correctamente" |
| CP-MOV-09 | Juan repite el mismo horario | Mensaje de cruce de horario del backend |
| CP-MOV-10 | "Mis reservas" y cancelar la reserva | Estado pasa a "Cancelada" |
| CP-MOV-11 | Admin abre Zonas comunes | Botones "Solo para residentes" deshabilitados |
| CP-MOV-12 | Con `JWT_EXPIRES_IN=10s`, esperar y abrir Zonas | Aviso de sesión vencida y vuelve al Login |

## Limitaciones conocidas

- Datos del backend **en memoria**: al reiniciar el servidor se pierden las reservas.
- Contraseñas en texto plano y sin roles granulares en el backend (pendiente).
- Sin ícono de lanzador propio (Android Studio > New > Image Asset).
- `usesCleartextTraffic="true"` solo para desarrollo (backend en HTTP).
- Código **no compilado** en el entorno donde se escribió: la primera compilación
  en Android Studio es parte de la verificación (ver el historial del proyecto).

## Hoja de ruta

- [x] Fase 0 — Organización (`.gitignore`, README, estructura)
- [x] Fase 1 — Base técnica (sesión persistente, `ApiClient` genérico, 401/403, menú por rol)
- [x] Fase 2 — Zonas Comunes y Reservas (pendiente de verificar en emulador)
- [ ] Fase 3 — Residente: PQR y Comunicados
- [ ] Fase 4 — Vigilante: Visitantes y Vehículos
- [ ] Fase 5 — Residente: Cuentas de cobro y Pagos (solo lectura)
