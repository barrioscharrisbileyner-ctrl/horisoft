# Controles de seguridad

## Configuración y secretos

- Django carga `.env` desde la carpeta del proyecto; variables del proceso
  tienen prioridad.
- En `DJANGO_ENV=production` el arranque exige una clave de al menos 50
  caracteres y `DJANGO_ALLOWED_HOSTS`.
- Mantén `.env`, respaldos, datos personales y claves fuera del control de
  versiones. La cuenta de base de datos de producción debe tener permisos
  mínimos y una contraseña propia.
- Ejecuta `manage.py check --deploy --fail-level WARNING` antes de desplegar.

## Autenticación y solicitudes

- La API usa JWT con tokens de acceso de 15 minutos y renovación rotativa.
- El login está limitado por DRF y el proxy Nginx; el refresh también tiene un
  límite específico.
- En Docker, Redis proporciona caché compartida para las cuotas de DRF.
  En desarrollo sin Redis, el fallback en memoria no comparte cuotas entre
  procesos.
- DRF pagina las listas a 20 elementos. Las vistas web mantienen CSRF y
  autenticación de sesión.
- Los permisos API son por rol y copropiedad. Las relaciones seleccionables en
  los endpoints también se limitan a las copropiedades autorizadas.
- Los usuarios administrativos reciben accesos explícitos mediante
  `AccesoPropiedad`; residentes solo heredan acceso de sus residencias activas.
  Las vistas, formularios, API y administración aplican el mismo alcance.
- El acceso de compatibilidad sin fila `AccesoPropiedad` solo se concede si
  existe exactamente una copropiedad. Al crear la segunda, asigna accesos
  explícitos a la copropiedad existente antes de crearla, para evitar
  ambigüedades o perder accesos.

## Auditoría

`auditoria.AuditEvent` conserva actor, método, ruta, código de respuesta y
fecha para peticiones de escritura. No registra contraseñas, tokens ni cuerpos
de formulario. Como los eventos no guardan una copropiedad, solo un
superusuario puede consultarlos; no se pueden crear, modificar ni borrar desde
la interfaz de administración.

## Archivos

- El módulo documental acepta PDF de hasta 10 MiB y valida extensión y firma.
- Los archivos están en `MEDIA_ROOT` privado; no se publican con una URL de
  almacenamiento. La descarga pasa por una vista protegida por rol, se entrega
  como adjunto y usa `X-Content-Type-Options: nosniff`.
- Los enlaces externos deben usar HTTPS. Mantén el límite de Nginx coherente
  con el tamaño máximo y el overhead multipart.

## Base de datos y despliegue

- Haz un respaldo antes de aplicar migraciones o restaurar datos.
- El servicio web no migra automáticamente al arrancar; usa el perfil
  `maintenance` explícitamente después de respaldar.
- El puerto HTTP de Compose escucha en loopback. Expón el servicio solo a
  través de un terminador TLS confiable y configura `X-Forwarded-Proto`.
- Revisa `docker compose logs` y conserva los respaldos fuera del volumen de
  base de datos.

## Migración a aislamiento multi-copropiedad

Las migraciones asignan automáticamente filas antiguas sin copropiedad solo
cuando hay exactamente una copropiedad. Si hay más de una, asigna manualmente
los registros de catálogo, las personas y los accesos de usuarios no
residentes antes de reintentar `manage.py migrate`. Las tablas nuevas quedan
creadas por las migraciones previas antes de que falle la migración de
asignación. En el shell de Django, asigna cada registro de catálogo con
`obj.propiedad_horizontal = propiedad` y guarda; para personas usa
`persona.propiedades.add(propiedad)` y para usuarios no residentes crea su
`AccesoPropiedad` correspondiente. No apliques la migración en producción sin
respaldo ni ignores un error de asignación.
