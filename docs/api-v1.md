# API REST v1

Base URL: `/api/v1/`. La especificación OpenAPI está disponible en
`GET /api/v1/schema/`.

## Autenticación

1. `POST /api/v1/auth/login/` recibe `username` y `password`; devuelve `access`,
   `refresh` y el resumen del usuario.
2. Envía `Authorization: Bearer <access>` a las rutas protegidas.
3. `POST /api/v1/auth/refresh/` recibe `refresh` y devuelve un nuevo `access`.
4. `GET /api/v1/auth/me/` devuelve el perfil asociado al token.

Los tokens de acceso expiran en 15 minutos. El login y refresh tienen límites
de uso. Las respuestas de listas están paginadas con 20 resultados (`count`,
`next`, `previous`, `results`).

## Endpoints

| Método | Ruta | Rol / acceso | Descripción |
|---|---|---|---|
| `GET` | `/health/` | Público | Estado del servicio |
| `POST` | `/auth/login/` | Público; con límite de tasa | Obtener JWT |
| `POST` | `/auth/refresh/` | Refresh token; con límite de tasa | Renovar JWT |
| `GET` | `/auth/me/` | Autenticado | Datos básicos del usuario y residencias |
| `GET` | `/residentes/me/` | Residente | Datos básicos del residente |
| `GET` | `/zonas-comunes/` | Administrador, Administrativo, Residente, Vigilante | Zonas de las copropiedades autorizadas |
| `GET`, `POST` | `/reservas/` | Administrador, Administrativo, Residente, Vigilante | Listar y crear reservas |
| `GET` | `/reservas/{id}/` | Roles autorizados | Detalle dentro del ámbito del usuario |
| `POST` | `/reservas/{id}/cancelar/` | Administrador, Administrativo, Residente | Cancelar; residente solo cancela las propias |
| `GET`, `POST` | `/pqrs/` | Administrador, Residente, Vigilante | Listar y crear PQR |
| `GET` | `/comunicados/` | Administrador, Administrativo, Residente, Vigilante | Comunicados publicados para el rol y copropiedad |
| `GET` | `/schema/` | Público | Esquema OpenAPI JSON |

Ejemplo de creación de reserva:

```json
{
  "zona": 1,
  "residencia": 1,
  "fecha": "2026-12-10",
  "hora_inicio": "09:00",
  "hora_fin": "10:00",
  "observaciones": "Reserva de prueba"
}
```

La API reutiliza `ReservaForm` para comprobar estado de la zona, copropiedad,
horario, fecha y cruces. Las PQR no aceptan `estado` ni `respuesta` desde el
cliente. Todas las relaciones se limitan a las copropiedades autorizadas; el
residente solo puede crear y consultar registros de sus residencias.

Errores comunes:

- `401`: falta el token o expiró y no pudo renovarse.
- `403`: el rol no tiene permiso.
- `400`: datos inválidos; DRF devuelve los errores por campo en español.
- `404`: el recurso no existe o está fuera del ámbito del usuario.
