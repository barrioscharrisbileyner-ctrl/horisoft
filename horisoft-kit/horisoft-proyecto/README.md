# Horisoft — Sistema de administración de propiedad horizontal

Proyecto Django del sistema **Horisoft**, construido siguiendo el patrón de la
guía **TallerExpress** (Entrega 2: capa web CRUD / Entrega 3: pruebas y
versionamiento). Proyecto formativo SENA — Tecnólogo en Análisis y Desarrollo de
Software (ADSO), Regional Quindío.

Entorno: Windows · Python · VS Code · **Laragon (MySQL)** · Django · Git.

## Módulos construidos (Django + MySQL)

| Módulo | App | Qué incluye | Pruebas |
|---|---|---|---|
| Residentes y Unidades | `residentes/` | CRUD de Personas, Unidades Residenciales y Residencias; reglas de negocio en `clean()` | Plan manual CP-01 a CP-09 + 10 automáticas |
| Autenticación y Roles | `usuarios/` | Login con correo, 5 roles, gestión de usuarios, decorador `@rol_requerido()` | CP-10 a CP-19, CP-32 |
| Zonas Comunes y Reservas (RQ03) | `reservas/` | CRUD de zonas, reservas con reglas de negocio, confirmar/cancelar, vista por rol | CP-20 a CP-29 |
| Protección de Residentes por rol | `residentes/` | Las vistas exigen sesión y rol | CP-30, CP-31 |

La app móvil Android (`app-movil/`) consume el prototipo Express: Login, Zonas Comunes y Reservas.

Los demás módulos (PQR, Gestión Financiera, Comunicaciones, Gestión Documental,
Seguridad, Inventario, Proveedores y Administrativo) existen como **prototipo
Express** en `backend-node/` y se migran a Django en ese orden.

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
> instalación tiene una contraseña distinta, edítala en
> `horisoft/settings.py` → `DATABASES`.

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

Los archivos de migración ya están en el repositorio (`residentes`, `usuarios`
y `reservas`); no hace falta `makemigrations` salvo que cambies un modelo.
Se crean las tablas `residentes_*`, `usuarios_perfilusuario`,
`reservas_zonacomun` y `reservas_reserva`, además de las de Django (auth,
sesiones, admin).

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

## 4. Pruebas (Entrega 3)

### 4.1 Pruebas automáticas

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

### 4.2 Plan de pruebas manual — Residentes (plantilla)

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

### 4.3 Versionamiento con Git

```bash
git init
git add .
git commit -m "Modulo Residentes y Unidades de Horisoft (CRUD)"

git remote add origin https://github.com/TU_USUARIO/horisoft.git
git branch -M main
git push -u origin main
```

Recuerda dejar el repositorio **público** para que el instructor pueda
revisarlo, y no subir contraseñas reales (en este entorno académico,
Laragon no tiene contraseña, así que no hay secreto que exponer).

### 4.4 Empaquetar

```bash
pip freeze > requirements.txt
```

Comprime el proyecto **sin** la carpeta `.venv/` con el nombre que pida tu
instructor (ej. `NOMBREAPELLIDO_AA2_EV02.zip`) y sube según corresponda.

## 5. Prototipo Express (`backend-node/`)

Backend en Node.js/Express con arquitectura por capas
(`routes → middlewares → controllers → services → data`) que implementa y valida
las reglas de negocio de los 14 módulos, con autenticación **JWT** real
(`jsonwebtoken`): lectura pública, escritura protegida. Los datos viven en
memoria (sin MySQL). Es la referencia para migrar cada módulo a Django.

```bash
cd backend-node
copy .env.example .env      # y define JWT_SECRET
npm install
npm run dev                 # http://localhost:3000
node pruebas-jwt.js         # también pruebas-jwt-modulos.js, -pqr.js, -resto.js, -residencia.js y pruebas-manuales.js
```

## 6. App móvil (`app-movil/`)

Abre la carpeta en Android Studio y ejecútala en un emulador con el backend Express encendido
(`npm run dev` en `backend-node/`). El emulador llega a tu computador por `10.0.2.2:3000`
(constante `BASE_URL` en `ApiClient.java`). Usuarios de prueba del backend Express:
`juan.perez@horisoft.com` / `juan123` (Residente) y `admin@horisoft.com` / `admin123`.

## 7. Siguientes módulos

Mismo patrón (modelo → ModelForm con `clean()` → vistas con `@rol_requerido` →
plantillas Bootstrap → pruebas CP-xx → commit), en este orden: PQR →
Gestión Financiera (incluye Multa y Convenio de Pago) → Comunicaciones →
Gestión Documental → Seguridad (incluye Cámara) → Inventario → Proveedores →
Administrativo. La numeración de pruebas continúa desde **CP-33**.
