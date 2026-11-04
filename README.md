# Horisoft — Sistema de administración de propiedad horizontal

Proyecto Django del sistema **Horisoft**, construido siguiendo el patrón de la
guía **TallerExpress** (Entrega 2: capa web CRUD / Entrega 3: pruebas y
versionamiento). Proyecto formativo SENA — Tecnólogo en Análisis y Desarrollo de
Software (ADSO), Regional Quindío.

Entorno: Windows · Python · VS Code · **Laragon (MySQL)** · Django · Git.

## Módulos implementados (Django)

| Módulo | App | Funcionalidad principal |
|---|---|---|
| Residentes y Unidades | `residentes/` | Personas, copropiedades, unidades y residencias |
| Autenticación y Roles | `usuarios/` | Inicio de sesión, perfiles, roles y permisos |
| Zonas Comunes y Reservas | `reservas/` | Zonas, disponibilidad y reservas |
| PQR | `pqrs/` | Registro, respuesta y cierre de solicitudes |
| Gestión Financiera | `financiera/` | Cuentas de cobro, pagos inmutables, multas y convenios de pago |
| Comunicaciones | `comunicaciones/` | Publicación y archivo de comunicados |
| Gestión Documental | `documental/` | Enlaces HTTPS y PDF privados autenticados |
| Seguridad | `seguridad/` | Vigilantes, visitantes, cámaras y vehículos |
| Inventario | `inventario/` | Elementos y estados |
| Proveedores | `proveedores/` | Registro y estado de proveedores |
| Configuración | `configuracion/` | Parámetros administrativos |
| API REST v1 | `api_v1/` | JWT, paginación, límites por rol/IP y esquema OpenAPI |
| Auditoría | `auditoria/` | Registro de operaciones de escritura sin guardar payloads |

La app móvil Android (`app-movil/`) consume la API JWT de Django para login,
zonas comunes y reservas. `backend-node/` se conserva como prototipo separado.

El backend Express (`backend-node/`) permanece como prototipo de referencia; el
backend oficial del proyecto es Django.

## 1. Estructura del proyecto

```
horisoft/
├── manage.py
├── requirements.txt
├── .gitignore
├── horisoft/              <- configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── residentes/            <- Residentes y Unidades
│   ├── models.py          <- PropiedadHorizontal, Persona, UnidadResidencial, Residencia
│   ├── forms.py           <- ModelForm + reglas de negocio (clean())
│   ├── views.py           <- vistas protegidas con @rol_requerido
│   ├── urls.py · admin.py · tests.py · migrations/
│   └── templates/residentes/   (base.html es la base de TODO el sistema)
├── usuarios/              <- Autenticación y Roles
│   ├── models.py          <- PerfilUsuario (rol + Persona vinculada)
│   ├── permisos.py        <- matriz de permisos por rol (un solo lugar)
│   ├── decorators.py      <- @rol_requerido(...)
│   ├── forms.py · views.py · urls.py · tests.py · migrations/
│   ├── management/commands/crear_administrador.py
│   └── templates/
├── reservas/              <- Zonas Comunes y Reservas
│   ├── models.py          <- ZonaComun, Reserva
│   ├── forms.py           <- reglas de negocio de la reserva (clean())
│   ├── views.py · urls.py · admin.py · tests.py · migrations/
│   └── templates/reservas/
├── backend-node/          <- prototipo Express + JWT (reglas de negocio de los 14 módulos)
└── app-movil/             <- app Android (Java): Login y Zonas Comunes / Reservas
```

> El entorno oficial y obligatorio es **Python · Django · MySQL**. El backend
> Express (`backend-node/`) es un prototipo de las reglas de negocio, no el
> sistema final.

## 2. Preparar el entorno (Entrega 1 — base del proyecto)

### 2.1 Iniciar Laragon y crear la base de datos

1. Abre **Laragon** y arranca **MySQL** (botón "Start All" o solo MySQL).
2. Abre **HeidiSQL** o **phpMyAdmin** desde el menú de Laragon (botón
   derecho → MySQL → HeidiSQL).
3. Crea una base de datos nueva llamada **`horisoft_db`**
   (colación recomendada: `utf8mb4_general_ci`).

> Laragon por defecto usa el usuario `root` **sin contraseña**. Si tu
> instalación tiene una contraseña distinta, configúrala en el archivo `.env`.
> Para producción crea un usuario MySQL propio con permisos mínimos.

### 2.2 Entorno virtual e instalación

La compatibilidad declarada es Python 3.10–3.13. El kit se validó en Python
3.13.7 con Django 5.2.18.

Desde la carpeta `horisoft/` (donde está `manage.py`), en la terminal de
VS Code:

```bash
python -m venv .venv
.venv\Scripts\activate          # En Windows
pip install -r requirements.txt
```

> **Nota:** este proyecto usa `PyMySQL` (driver puro de Python) en vez de
> `mysqlclient`, porque `mysqlclient` exige tener instalado Microsoft
> Visual C++ Build Tools en Windows para compilar, y eso suele fallar en
> equipos sin esas herramientas. `PyMySQL` no necesita compilar nada.
> El archivo `horisoft/__init__.py` ya incluye el "shim" necesario:
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

### 2.3 Migraciones

```bash
python manage.py migrate
```

Las migraciones versionadas cubren todas las apps con modelos. Haz una copia de
seguridad antes de aplicar cambios sobre una base de datos real.

### 2.4 Primer usuario Administrador

El sistema exige iniciar sesión. Crea el primer administrador (pide la
contraseña por consola):

```bash
python manage.py crear_administrador --correo tu@correo.com --nombre "Tu Nombre"
```

> Las contraseñas pasan por los validadores de Django: mínimo 8 caracteres,
> no demasiado comunes ni solo numéricas.
>
> Para usar el panel `/admin/` de Django, crea además un superusuario con
> `python manage.py createsuperuser` (opcional).

## 3. Levantar el servidor (Entrega 2)

```bash
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` e inicia sesión. Cada rol llega a su sección:

| Dirección | Qué es | Quién entra |
|---|---|---|
| `/usuarios/login/` | Inicio de sesión | Todos |
| `/residentes/` · `/personas/` · `/unidades/` · `/residencias/` | Residentes y Unidades | Administrador y Administrativo (todo); Vigilante (solo consulta) |
| `/reservas/zonas/` | Zonas comunes | Todos menos Proveedor (gestionan Administrador y Administrativo) |
| `/reservas/` | Reservas | Administrador y Administrativo (todas); Residente (las suyas); Vigilante (consulta) |
| `/usuarios/` | Gestión de usuarios | Solo Administrador |
| `/usuarios/panel/` | Panel de gestión y resumen | Administrador y Administrativo |
| `/admin/` | Panel de Django | Superusuario |

### Matriz de permisos por rol

| Acción | Administrador | Administrativo | Residente | Vigilante | Proveedor |
|---|:-:|:-:|:-:|:-:|:-:|
| Consultar Residentes, Unidades y Residencias | ✔ | ✔ | — | ✔ | — |
| Crear / editar / eliminar Residentes, Unidades, Residencias | ✔ | ✔ | — | — | — |
| Gestionar zonas comunes | ✔ | ✔ | — | — | — |
| Ver zonas comunes | ✔ | ✔ | ✔ | ✔ | — |
| Ver reservas | todas | todas | solo las suyas | todas | — |
| Crear reserva | ✔ | ✔ | ✔ (con sus residencias) | — | — |
| Confirmar reserva | ✔ | ✔ | — | — | — |
| Cancelar reserva | ✔ | ✔ | ✔ (solo las suyas) | — | — |
| Eliminar reserva · gestionar usuarios | ✔ | — | — | — | — |
| Consultar cuentas, pagos, multas y convenios propios | ✔ | ✔ | ✔ | — | — |
| Gestionar cuentas, pagos, multas y convenios | ✔ | ✔ | — | — | — |
| Consultar visitantes, cámaras y vehículos de su copropiedad | ✔ | ✔ | ✔ | ✔ | — |
| Registrar/gestionar vehículos propios | ✔ | ✔ | ✔ | — | — |
| Gestionar cámaras | ✔ | ✔ | — | — | — |
| Panel Administrativo | ✔ | ✔ | — | — | — |

La matriz vive en `usuarios/permisos.py`; se ajusta en un solo lugar.

### Flujo recomendado para probar

1. Crea 2 o 3 **Unidades** (ej. 101, 102, 201) y 2 o 3 **Residentes** (Personas).
2. En **Residencias** → "Asociar residente a unidad", enlázalos con un rol.
   Intenta asociar dos personas distintas como "Propietario" de la misma unidad →
   debe mostrar el mensaje de validación.
3. En **Usuarios** (como Administrador) crea un usuario con rol **Residente**,
   vinculado a una de esas personas.
4. Crea 2 o 3 **Zonas comunes** (una en "Mantenimiento").
5. Entra como ese Residente: reserva una zona; prueba un cruce de horario, una
   fecha pasada y la zona en mantenimiento → cada caso muestra su mensaje.
6. Entra como Administrativo y confirma la reserva.

### Datos de demostración (opcional)

Para recorrer el sistema sin crear todo a mano (por ejemplo, para tomar capturas):

```bash
python manage.py crear_datos_demo --paginacion
```

Crea la copropiedad, 3 unidades, 2 residentes con su residencia, 3 zonas comunes (una en
mantenimiento), una reserva de Luis y un usuario por rol. La contraseña de todos es
`Horisoft#2026`. Es idempotente y solo para entornos de prueba.

## 4. Preparación para producción

El proyecto ya quedó preparado para despliegues reales con una base mínima de hardening:

- `DEBUG` desactivado por defecto en producción.
- `SECURE_*` habilitados con variables de entorno.
- `WhiteNoise` para servir archivos estáticos en producción.
- `Gunicorn` como servidor WSGI.
- `Dockerfile` y `docker-compose.yml` para despliegue simple.

### 4.1 Variables de entorno

Copia el ejemplo a `.env` y ajusta los valores reales antes de ejecutar Django:

```bash
copy .env.example .env
```

Genera la clave de Django en tu terminal y cópiala directamente a `.env`; no
la publiques ni la compartas:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`horisoft/settings.py` carga el archivo `.env` local (las variables ya
definidas por el proceso tienen prioridad). Para Laragon configura `MYSQL_HOST`,
`MYSQL_PORT`, `MYSQL_NAME`, `MYSQL_USER` y `MYSQL_PASSWORD` con los datos de esa
instalación. No uses la cuenta `root` ni contraseñas vacías fuera del equipo de
desarrollo.

En producción:

- `DJANGO_ENV=production`
- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<secreto aleatorio de al menos 50 caracteres>`
- `DJANGO_ALLOWED_HOSTS=tu-dominio.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://tu-dominio.com`
- `DJANGO_SECURE_SSL_REDIRECT=True`
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_NAME`, `MYSQL_USER`, `MYSQL_PASSWORD`

Los comandos `manage.py test` usan SQLite para no escribir datos de prueba en
Laragon. Los demás comandos usan el motor configurado en `.env`.

### 4.2 Docker Compose con MySQL y Nginx

Completa `DOCKER_DB_USER`, `DOCKER_DB_PASSWORD` y
`DOCKER_DB_ROOT_PASSWORD` con credenciales distintas y fuertes. La pila publica
Nginx solo en `127.0.0.1:8080` por defecto y está pensada para quedar detrás de
un terminador TLS confiable en el mismo equipo. No expongas ese puerto a
Internet sin TLS y sin configurar el proxy para enviar
`X-Forwarded-Proto: https`.

La primera vez, inicializa la base y aplica las migraciones de forma explícita:

```bash
docker compose up -d db
docker compose --profile maintenance run --rm migrate
docker compose up --build -d web nginx
```

Los archivos cargados se guardan en un volumen privado y solo se entregan por
una vista autenticada. Se permiten PDF de hasta 10 MB; se verifica la firma del
archivo y las descargas se fuerzan como adjunto. Los enlaces heredados deben
usar HTTPS.

Para revisar los logs:
```bash
docker compose logs -f web nginx
```

Para respaldar o restaurar la base Docker:

```bash
python scripts/backup_db.py backups/horisoft.sql
python scripts/restore_db.py backups/horisoft.sql --confirm-database horisoft_db
```

La restauración exige confirmar el nombre exacto de la base y escribir
`RESTORE-<nombre>`; sobrescribe sus datos actuales.

### 4.3 API v1

La app móvil se conecta a Django. Métodos, rutas, permisos y ejemplos se
documentan en [docs/api-v1.md](docs/api-v1.md). Las listas tienen paginación de
20 elementos y las rutas protegidas aplican permisos por rol y copropiedad.
Incluye autenticación JWT, zonas comunes, reservas, PQR, comunicados y datos
básicos del residente.

### 4.4 Verificación

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

La validación de despliegue requiere `DJANGO_ENV=production`, una clave válida
y hosts definidos:

```bash
python manage.py check --deploy --fail-level WARNING
```

### 4.5 CI y cobertura

Instala requisitos de desarrollo y ejecuta la misma validación de CI:

```bash
pip install -r requirements-dev.txt
coverage run manage.py test
coverage report --fail-under=55
```

GitHub Actions ejecuta estas verificaciones para Python 3.10–3.13.

## 5. Pruebas (Entrega 3)

### 5.1 Pruebas automáticas
```bash
python manage.py test                # todo el proyecto
python manage.py test usuarios       # o una app: residentes / usuarios / reservas
```

| IDs | App | Qué verifican |
|---|---|---|
| (sin ID) | `residentes` | Reglas de residencia (sin duplicados ni dos propietarios) y CRUD (crear por POST, eliminar solo por POST, campos obligatorios) |
| CP-10 a CP-13 | `usuarios` | Registro: usuario válido, correo duplicado, contraseñas distintas, residente exige persona |
| CP-14, CP-15 | `usuarios` | Login correcto (correo sin distinguir mayúsculas), contraseña incorrecta y cuenta inactiva |
| CP-16, CP-17 | `usuarios` | Sin sesión redirige al login; `@rol_requerido` permite o responde 403 |
| CP-18, CP-19, CP-32 | `usuarios` | El administrador no puede bloquearse a sí mismo; comando `crear_administrador`; inicio por rol |
| CP-20 a CP-25 | `reservas` | Reglas de la reserva: válida, zona en mantenimiento, fecha pasada, horas, cruce de horario, residencia propia |
| CP-26 a CP-29 | `reservas` | Cada residente ve y cancela solo lo suyo; matriz de roles; no se borra lo que tiene reservas |
| CP-30, CP-31 | `residentes` | Las vistas de Residentes exigen sesión y rol |
| CP-33 | `reservas` | Se rechaza la hora exacta actual y se acepta el minuto siguiente |
| CP-34 | `financiera` | Multas y convenios; el total de convenios activos no supera el saldo y se cumple al pagar |
| CP-35 | `seguridad` | Placas colombianas, unicidad y vehículos limitados a la residencia del usuario |
| CP-36 | `usuarios` | Panel de gestión con datos agregados por copropiedad y acceso restringido por rol |

### 5.2 Plan de pruebas manual — Residentes (plantilla)

Ejecuta cada caso y anota el resultado obtenido:

| ID | Caso de prueba | Pasos | Resultado esperado | Resultado obtenido | Estado |
|----|------------------|-------|----------------------|----------------------|--------|
| CP-01 | Crear residente válido | Llenar formulario completo y Guardar | El residente se guarda y aparece en la lista | | |
| CP-02 | Crear residente sin documento | Dejar "Número de documento" vacío y Guardar | No guarda; muestra "Este campo es obligatorio." | | |
| CP-03 | Crear unidad válida | Llenar número y tipo, Guardar | La unidad se guarda y aparece en la lista | | |
| CP-04 | Asociar residente a unidad | Elegir persona, unidad y rol, Guardar | Se crea la residencia y aparece en la lista | | |
| CP-05 | Dos propietarios en la misma unidad | Asociar persona A como Propietario, luego persona B como Propietario de la misma unidad | Muestra el error de validación y no guarda | | |
| CP-06 | Residencia duplicada | Asociar la misma persona, misma unidad, mismo rol dos veces | Muestra el error de validación y no guarda | | |
| CP-07 | Listar con paginación | Crear más de 10 residentes, abrir la lista | Muestra 10 por página y los controles de paginación | | |
| CP-08 | Editar residente | Abrir un residente, cambiar el teléfono, Guardar | El cambio queda reflejado en la lista | | |
| CP-09 | Eliminar con confirmación | Pulsar Eliminar | Pide confirmación; al aceptar, lo quita de la lista | | |

> Si algún caso queda en "No cumple", documéntalo igual que en el ejemplo
> (CP-07 de TallerExpress): no se oculta, se reporta como hallazgo o
> mejora pendiente.

### 5.3 Versionamiento con Git

```bash
git init
git add .
git commit -m "Modulo Residentes y Unidades de Horisoft (CRUD)"

git remote add origin https://github.com/TU_USUARIO/horisoft.git
git branch -M main
git push -u origin main
```

No hagas público el repositorio sin revisar primero permisos, datos personales,
credenciales, archivos `.env`, respaldos y evidencias. No publiques secretos
reales ni bases de datos.

### 5.4 Empaquetar

```bash
pip install -r requirements-dev.txt
```

Comprime el proyecto **sin** la carpeta `.venv/` con el nombre que pida tu
instructor (ej. `NOMBREAPELLIDO_AA2_EV02.zip`) y sube según corresponda.

## 6. Prototipo Express (`backend-node/`)

Backend en Node.js/Express con arquitectura por capas
(`routes → middlewares → controllers → services → data`) que implementa y valida
las reglas de negocio de los 14 módulos. Se conserva como prototipo de
referencia; Django + MySQL es el backend oficial y no se migrarán datos
persistentes desde Express. Los datos viven en memoria y sus lecturas de módulo
son públicas, por lo que no debe exponerse con información real.

```bash
cd backend-node
copy .env.example .env      # define una JWT_SECRET local fuerte
npm install
npm run dev                 # prototipo solo para desarrollo
npm test                    # suites de integración
```

Los usuarios y claves de demostración se cargan solo con `NODE_ENV=development`
o `test`. Fuera de esos entornos se exige `HORISOFT_ADMIN_EMAIL` y una clave
`HORISOFT_ADMIN_PASSWORD` de al menos 12 caracteres. Las contraseñas se
almacenan con bcrypt. `npm audit --omit=dev` no reporta vulnerabilidades; la
auditoría completa conserva dos advisories moderados en `minimatch` transitivo
de `nodemon`, documentados en [backend-node/README.md](backend-node/README.md).

## 7. App móvil (`app-movil/`)

La app consume la API JWT oficial de Django. Inicia Django con
`python manage.py runserver` y abre `app-movil/` en Android Studio. El emulador
usa `http://10.0.2.2:8000/api/v1`; para un teléfono físico configura la IP del
equipo en `ApiClient.BASE_URL`. El APK debug se genera con
`gradlew.bat assembleDebug` desde `app-movil/`. La compilación se verificó; el
flujo todavía debe probarse visualmente en un emulador/dispositivo.

## 8. Evidencias y documentación

Consulta [docs/arquitectura.md](docs/arquitectura.md),
[docs/seguridad.md](docs/seguridad.md), [docs/api-v1.md](docs/api-v1.md) y
[docs/evidencias-sena.md](docs/evidencias-sena.md) para el diseño, controles y
evidencias que se pueden generar sin exponer datos reales. La
[memoria del proyecto](Horisoft_Memoria_del_Proyecto.md) es la fuente de verdad
del estado, pruebas e incidencias. El
[guion de demostración](docs/guion_video_demostracion.md) propone un recorrido
de seis minutos; los manuales de usuario/técnico están en `docs/` en formato
Word. Se regeneran con `cd backend-node; npm run docs:generate` usando la
librería Node `docx`; los marcadores de captura deben reemplazarse solo con
imágenes reales del aprendiz.
