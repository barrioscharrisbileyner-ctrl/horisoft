# Horisoft — App móvil Android

App Android (Java + XML, sin librerías externas) que consume la API oficial
Django con JWT de Horisoft. Paquete: `com.horisoft.app`.

## Qué incluye hoy

| Módulo | Pantallas | Endpoints |
|---|---|---|
| Autenticación | Login, renovación JWT, sesión persistente y Home por rol | `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`, `GET /api/v1/auth/me/` |
| Zonas Comunes y Reservas (RQ03) | Zonas comunes, Nueva reserva, Mis reservas (con cancelar) | `GET /api/v1/zonas-comunes/`, `GET/POST /api/v1/reservas/`, `POST /api/v1/reservas/{id}/cancelar/` |

## Cómo ejecutarla

1. **Backend:** inicia el proyecto Django desde la carpeta que contiene
   `manage.py`, ejecuta `python manage.py migrate` y luego `python manage.py runserver`.
2. **App:** abre la carpeta `app-movil/` en Android Studio, espera el *Gradle Sync*
   y ejecuta en un emulador. La compilación debug está verificada; el flujo
   visual de la versión integrada con Django queda pendiente de prueba en emulador.
3. **URL del servidor:** `ApiClient.BASE_URL` usa `http://10.0.2.2:8000/api/v1`
   en el emulador. Para un teléfono físico cambia el host por la IP del equipo
   y confirma que Django permita ese host y el tráfico HTTP de desarrollo.

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

## Decisiones anteriores (reemplazadas por la integración Django)

- El token se guarda **tal como lo entrega el backend** (`"Bearer eyJ..."`) y se envía
  sin modificarlo en el header `Authorization`.
- El formulario envía la residencia activa y Django valida que pertenezca a la
  persona autenticada.
- Los mensajes de las reglas de negocio (cruce de horario, zona en mantenimiento,
  fecha pasada) los valida el backend y la app los muestra tal cual.
- Todas las rutas de la app requieren autenticación; Django aplica permisos y
  aislamiento por copropiedad.

## Integración oficial vigente

- `ApiClient.BASE_URL` apunta a Django en `http://10.0.2.2:8000/api/v1` para el
  emulador. En un teléfono físico cambia el host por la IP local del equipo.
- El login envía `username` y `password`; Django devuelve `access`, `refresh` y
  el resumen del usuario. La app conserva ambos tokens y renueva el acceso una
  vez si una solicitud protegida recibe HTTP 401.
- Las respuestas de listas usan la paginación DRF (`results`). Reservas,
  creación y cancelación se realizan en `api/v1/`; la API verifica rol,
  residencia y copropiedad en el servidor.
- Para ejecutar la aplicación, levanta Django con `python manage.py runserver`
  y abre `app-movil/` en Android Studio. La prueba visual en emulador queda
  pendiente hasta ejecutar ese entorno.
- El APK debug compilado se genera en
  `app/build/outputs/apk/debug/app-debug.apk` desde la carpeta `app-movil/`
  con `gradlew.bat assembleDebug`.

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
| CP-MOV-12 | Dejar vencer el token de acceso y abrir Zonas | Renueva el token con el refresh y carga la lista; si el refresh venció, vuelve al Login |

## Limitaciones conocidas

- Express conserva sus datos en memoria; la app móvil ya no lo utiliza.
- `usesCleartextTraffic="true"` solo para desarrollo (backend en HTTP).
- La experiencia visual en emulador debe verificarse manualmente.

## Hoja de ruta

- [x] Fase 0 — Organización (`.gitignore`, README, estructura)
- [x] Fase 1 — Base técnica (sesión persistente, `ApiClient` genérico, 401/403, menú por rol)
- [x] Fase 2 — Zonas Comunes y Reservas (pendiente de verificar en emulador)
- [ ] Fase 3 — Residente: PQR y Comunicados
- [ ] Fase 4 — Vigilante: Visitantes y Vehículos
- [ ] Fase 5 — Residente: Cuentas de cobro y Pagos (solo lectura)
