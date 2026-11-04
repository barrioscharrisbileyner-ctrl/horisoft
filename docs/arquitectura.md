# Arquitectura de Horisoft

## Componentes

- **Django 5.2** es el backend de referencia y contiene las reglas de negocio.
- **Django REST Framework** publica la API bajo `/api/v1/`; SimpleJWT emite
  tokens de acceso y renovación.
- **MySQL** es el motor de producción. Laragon puede proveerlo en desarrollo;
  Docker Compose define una instancia MySQL 8.4 con volumen persistente.
- **Gunicorn** ejecuta WSGI; **WhiteNoise** entrega los recursos estáticos.
- **Nginx** sirve de proxy inverso y aplica un límite de solicitudes al login.
  Compose lo enlaza a `127.0.0.1` para que un terminador TLS local y confiable
  sea quien exponga el servicio.
- **Redis** comparte el estado de throttling entre los procesos Gunicorn en
  Compose. Sin `REDIS_URL`, el entorno de desarrollo usa la caché local de
  Django.

## Aplicaciones

| App | Responsabilidad |
|---|---|
| `residentes` | Propiedad horizontal, personas, unidades y residencias |
| `usuarios` | Perfiles, roles, autenticación y permisos web |
| `reservas` | Zonas comunes y reservas |
| `pqrs` | Solicitudes, quejas, reclamos y sugerencias |
| `financiera` | Cuentas de cobro, pagos, multas y convenios de pago |
| `comunicaciones` | Comunicados |
| `documental` | Documentos y descargas privadas |
| `seguridad` | Vigilantes, visitantes, cámaras y vehículos |
| Panel Administrativo | Resumen operativo para Administrador y Administrativo |
| `inventario` | Elementos de inventario |
| `proveedores` | Proveedores |
| `configuracion` | Parámetros de configuración |
| `api_v1` | Serializadores, endpoints y JWT |
| `auditoria` | Eventos de solicitudes que modifican datos |

Cada aplicación conserva sus modelos, servicios, formularios/vistas y pruebas.
Las migraciones se mantienen en el repositorio y deben revisarse antes de
aplicarlas en una base con datos reales.

## Flujo de una solicitud

1. Nginx recibe la petición y, para el endpoint de login, aplica su límite por
   IP.
2. Gunicorn entrega la petición a Django; los controles de sesión/CSRF aplican
   a la interfaz web y JWT a la API.
3. Las vistas aplican rol y las reglas de acceso del dominio.
4. Los servicios/modelos validan datos y ejecutan transacciones cuando hay
   efectos contables o reservas concurrentes.
5. El middleware registra método, ruta, actor y código HTTP para solicitudes
   de escritura, sin guardar el cuerpo de la petición.

## Alcance de aislamiento por copropiedad

`UnidadResidencial` y los catálogos de zonas, comunicaciones, documentos,
vigilantes, inventario, proveedores y configuración pertenecen a una
`PropiedadHorizontal`. Reservas, PQR, cuentas, pagos y visitantes obtienen la
copropiedad mediante sus relaciones con `ZonaComun` o `Residencia`.

`AccesoPropiedad` asigna a los usuarios no residentes sus copropiedades. El
acceso de los residentes se deriva de sus residencias activas. Las vistas,
formularios, endpoints API y listados del administrador filtran por ese
ámbito; las operaciones sobre registros ajenos responden como no encontrados.
Los superusuarios conservan acceso global para tareas de soporte.

Las migraciones agregan inicialmente las claves como anulables, asignan los
datos existentes solo cuando la asignación sea inequívoca y después las
convierten en obligatorias. Si hay varias copropiedades y quedan filas sin
asignar, la migración se detiene con un error explícito para permitir una
asignación manual antes de reintentarla. Realiza una copia de seguridad antes
de ejecutarlas en una base con datos reales.
