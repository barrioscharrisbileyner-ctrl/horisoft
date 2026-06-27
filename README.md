# Horisoft — Módulo Residentes y Unidades

Proyecto Django construido siguiendo el mismo patrón de la guía
**TallerExpress** (Entrega 2: capa web CRUD / Entrega 3: pruebas y
versionamiento), aplicado al sistema **Horisoft** (administración de
propiedad horizontal).

Entorno: Windows · Python · VS Code · **Laragon (MySQL)** · Django · Git.

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
└── residentes/            <- la app (módulo Residentes y Unidades)
    ├── models.py          <- PropiedadHorizontal, Persona, UnidadResidencial, Residencia
    ├── forms.py           <- ModelForm + reglas de negocio (clean())
    ├── views.py           <- 13 vistas (3 CRUD completos + inicio)
    ├── urls.py
    ├── admin.py
    ├── tests.py           <- pruebas automáticas
    ├── migrations/
    └── templates/residentes/
        ├── base.html
        ├── inicio.html
        ├── personas_lista.html / persona_form.html
        ├── unidades_lista.html / unidad_form.html
        └── residencias_lista.html / residencia_form.html
```

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
python manage.py makemigrations
python manage.py migrate
```

Esto crea en `horisoft_db` las tablas `residentes_propiedadhorizontal`,
`residentes_persona`, `residentes_unidadresidencial` y
`residentes_residencia`.

### 2.4 Usuario administrador (opcional, para usar /admin/)

```bash
python manage.py createsuperuser
```

## 3. Levantar el servidor (Entrega 2)

```bash
python manage.py runserver
```

Abre en el navegador:

- `http://127.0.0.1:8000/residentes/` → índice del módulo
- `http://127.0.0.1:8000/residentes/personas/` → CRUD de residentes
- `http://127.0.0.1:8000/residentes/unidades/` → CRUD de unidades
- `http://127.0.0.1:8000/residentes/residencias/` → asociar residente a unidad
- `http://127.0.0.1:8000/admin/` → panel de administración (con el superusuario)

### Flujo recomendado para probar

1. Crea 2 o 3 **Unidades** (ej. 101, 102, 201).
2. Crea 2 o 3 **Residentes** (Personas).
3. Ve a **Residencias** → "Asociar residente a unidad" y enlázalos con un
   rol (Propietario / Arrendatario / Familiar).
4. Intenta asociar dos personas distintas como "Propietario" de la misma
   unidad → debe mostrar el mensaje de validación.

## 4. Pruebas (Entrega 3)

### 4.1 Pruebas automáticas

```bash
python manage.py test residentes
```

Incluye pruebas de las reglas de negocio (no duplicar residencia, no dos
propietarios activos) y de las vistas CRUD (crear por POST, eliminar solo
por POST, validación de campos obligatorios).

### 4.2 Plan de pruebas manual (plantilla)

Repite el mismo formato de la guía TallerExpress. Ejecuta cada caso y
anota el resultado obtenido:

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

## 5. Siguientes módulos

Este mismo patrón (modelo → ModelForm con `clean()` → vistas GET/POST →
plantillas Bootstrap) se repite para los demás módulos de Horisoft:
Quejas y Solicitudes (PQR), Reservas de Zonas Comunes, Gestión Financiera
(Cuentas de Cobro / Pagos), Comunicaciones, etc. Cuando quieras, seguimos
con el siguiente módulo de la misma forma.
