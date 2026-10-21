# Kit Horisoft — Paso a paso para ejecutar todo y tomar las capturas

Evidencia GA9-220501096-AA3-EV02 · Reporte de plan de pruebas ejecutadas

Tiempo estimado: 40 a 60 minutos. Todo se hace con doble clic en los archivos `.bat` o, si prefieres,
con los comandos equivalentes que aparecen en cada paso.

---

## 0. Qué trae el kit

| Carpeta o archivo | Para qué sirve |
|---|---|
| `horisoft-proyecto/` | El proyecto completo y listo: Django (Residentes, Usuarios, Reservas), `backend-node/` (Express con las correcciones) y `app-movil/` (Android) |
| `1_VERIFICAR_ENTORNO.bat` | Prepara el entorno y comprueba que todo está listo |
| `2_PRUEBAS_DJANGO.bat` | Migra la base de datos y ejecuta las 40 pruebas de Django |
| `3_PRUEBAS_EXPRESS.bat` | Ejecuta las 6 pruebas de Express, con una pausa después de cada una |
| `4_SERVIDOR_CON_DATOS_DEMO.bat` | Carga datos de demostración y abre la aplicación en el navegador |
| `5_DEMOS_DE_DEFECTOS.bat` | Opcional: demuestra los defectos BUG-002, BUG-005 y BUG-006 |
| `herramientas/` | Scripts de apoyo que usan los `.bat` |
| `referencia_laboratorio/` | Los resultados que obtuve yo en mi entorno, para que compares con los tuyos |

## 1. Requisitos (instálalos una sola vez)

1. **Laragon** con MySQL. Es el que ya usas.
2. **Python 3.13** (también sirven 3.10, 3.11 o 3.12) desde python.org. En el instalador marca **Add python.exe to PATH**.
3. **Node.js LTS** desde nodejs.org.
4. **Android Studio**: solo si vas a hacer el Paso 6 (opcional).

## 2. Preparación (5 minutos)

1. Descomprime el zip en una ruta corta, **sin espacios ni tildes**. Por ejemplo `C:\horisoft-kit`.
2. Abre **Laragon** y presiona **Start All**. Comprueba que MySQL aparezca encendido.
3. Si vas a usar una carpeta de repositorio propia (`repo_django`), **no mezcles**: este kit trae su propia copia. Al final puedes copiar `horisoft-proyecto` sobre tu repositorio (sección 11).

---

## 3. Paso 1 — Verificar el entorno

Doble clic en **`1_VERIFICAR_ENTORNO.bat`**.

Crea el entorno virtual `.venv`, instala Django 5.2.18 y PyMySQL, y comprueba Python, MySQL y Node. Si la
base de datos `horisoft_db` no existe, la crea.

**Resultado esperado:** todas las líneas con `[ OK ]` y al final `todo listo`.

Si aparece `[FALLA]`, el mismo mensaje te dice qué hacer. Los casos más comunes están en la sección 10.

## 4. Paso 2 — Pruebas automáticas de Django (Figura 1)

Doble clic en **`2_PRUEBAS_DJANGO.bat`**.

(Equivale a: `python manage.py migrate` y `python manage.py test -v 2`, dentro de `horisoft-proyecto`
con el entorno `.venv` activado.)

**Resultado esperado al final:**

```
Ran 40 tests in 15.xxxs
OK
```

> **CAPTURA 1 (Figura 1):** la terminal mostrando `Ran 40 tests ... OK`. Si la lista es muy larga, toma dos
> capturas: el inicio y el final.

Las migraciones y el resultado de esta misma ejecucion se guardan en
`evidencias\django_pruebas.txt`.

## 5. Paso 3 — Pruebas de Express (Figuras 2 y 3)

Doble clic en **`3_PRUEBAS_EXPRESS.bat`**. Crea el `.env` si no existe, instala las dependencias y ejecuta 6
pruebas. Después de cada una se detiene: **presiona una tecla para pasar a la siguiente**.

| # | Archivo | Resultado esperado |
|---|---|---|
| 1 | `pruebas-jwt.js` | 11 correctas, 0 fallidas |
| 2 | `pruebas-jwt-modulos.js` | 7 correctas, 0 fallidas |
| 3 | `pruebas-jwt-pqr.js` | 6 correctas, 0 fallidas |
| 4 | `pruebas-jwt-resto.js` | 29 correctas, 0 fallidas |
| 5 | `pruebas-jwt-residencia.js` | 7 correctas, 0 fallidas |
| 6 | `pruebas-manuales.js` | 26 respuestas ✅ y 7 ❌ (los 7 son rechazos esperados, marcados «-> error») |

> **CAPTURA 2 (Figura 2):** las ejecuciones 1 a 5 (puedes tomar una captura por ejecución).
> **CAPTURA 3 (Figura 3):** la ejecución 6 completa.

**No muestres el archivo `.env` en ninguna captura.**

La salida completa de las seis suites se guarda tambien en
`evidencias\express_pruebas.txt`, y sigue apareciendo en pantalla para tomar capturas.

## 6. Paso 4 — La aplicación con datos de demostración (Figuras 4 a 8)

Doble clic en **`4_SERVIDOR_CON_DATOS_DEMO.bat`**. Carga los datos de prueba, abre el navegador en
`http://127.0.0.1:8000/` y deja el servidor encendido (para detenerlo: `Ctrl + C`).
Las migraciones, la carga de datos y la salida del servidor se guardan en
`evidencias\servidor_datos_demo.txt`.

**Usuarios de demostración** (contraseña de todos: `Horisoft#2026`):

| Rol | Correo |
|---|---|
| Administrador | `admin@horisoft.com` |
| Administrativo | `administrativo@horisoft.com` |
| Vigilante | `vigilante@horisoft.com` |
| Residente | `ana@horisoft.com` (Ana Pérez, unidad 101) |
| Residente | `luis@horisoft.com` (Luis Gómez, unidad 201) |

### 6.1 Plan manual CP-01 a CP-09 — como Administrador (`admin@horisoft.com`)

Anota el resultado de cada caso en tu tabla del reporte.

| ID | Qué hacer | Resultado esperado |
|---|---|---|
| CP-01 | **Residentes** → crear nuevo: documento `333`, nombre `Marta Ríos`, teléfono `3001234567` | Se guarda y aparece en la lista |
| CP-02 | Crear otro residente **sin** número de documento | No guarda; muestra «Este campo es obligatorio» |
| CP-03 | **Unidades** → crear: número `305`, tipo `Casa` | Se guarda y aparece en la lista |
| CP-04 | **Residencias** → asociar a `Marta Ríos` con la unidad `102` como `Arrendatario` | Se crea y aparece en la lista |
| CP-05 | Asociar a `Ana Pérez` a la unidad `201` como `Propietario` (Luis ya es el propietario) | Error de validación; no guarda |
| CP-06 | Asociar de nuevo a `Ana Pérez` a la `101` como `Propietario` | Error de validación («ya está asociada»); no guarda |
| CP-07 | Abrir la lista de **Residentes** | 10 por página, con controles de paginación (hay más de 10 personas) |
| CP-08 | Editar a `Marta Ríos` y cambiar su teléfono | El cambio se ve en la lista |
| CP-09 | Eliminar a `Residente Demo 11` | Pide confirmación; al aceptar, desaparece |

> **CAPTURA 8 (Figura 8):** tu tabla CP-01 a CP-09 con las columnas «Resultado obtenido» y «Estado» llenas.
> Te recomiendo además una captura del error de CP-05 como evidencia.

Cierra sesión (botón arriba a la derecha).

### 6.2 Como Residente (`ana@horisoft.com`)

Entra con Ana. Debe llevarte directo a **Reservas**.

1. **Cruce de horario (CP-24) → CAPTURA 4 (Figura 4).**
   Reservas → *Nueva reserva* → Salón Social, fecha de mañana, de `14:00` a `16:00`. Debe guardarse con un mensaje de éxito.
   Repite con `15:00` a `17:00`: debe mostrar **«Ya existe una reserva activa para esa zona en ese horario»**. Captura ese error.
2. **Zona en mantenimiento (CP-21) → CAPTURA 5 (Figura 5).**
   Nueva reserva → elige *Cancha Múltiple (Mantenimiento)*: debe mostrar que la zona no está disponible. Captura.
3. **Acceso denegado (CP-31) → CAPTURA 6 (Figura 6).**
   En la barra de direcciones escribe `http://127.0.0.1:8000/residentes/`: debe aparecer la página **403 Acceso denegado**. Captura.
4. **Solo ve lo suyo (CP-26) → CAPTURA 7 (Figura 7).**
   Abre *Reservas*: debe aparecer solo la reserva de Ana (Unidad 101). La reserva de Luis (Unidad 201) **no** debe verse. Captura.
5. Opcional (CP-27): cancela la reserva de Ana; el estado pasa a *Cancelada*.

### 6.3 Opcional: otros roles

- **Vigilante:** ve Residentes y Reservas, pero sin botones para crear, editar ni eliminar.
- **Administrativo:** puede confirmar la reserva de Ana (botón *Confirmar*).

---

## 7. Paso 5 (opcional) — Demostración de defectos

Doble clic en **`5_DEMOS_DE_DEFECTOS.bat`**.

- **Demo 1 (BUG-002, zona horaria):** en este kit el backend ya está corregido y debe decir `RESERVA ACEPTADA`.
  El defecto original solo aparece pasadas las 7:00 p.m. hora de Colombia; compara con
  `referencia_laboratorio\demo_zona_horaria_original.txt`.
- **Demo 2 (BUG-005 y BUG-006):** siguen abiertos. Debe mostrar `HTTP 201` con rol Residente y una contraseña en texto plano.
  Útil como evidencia de lo que queda pendiente.

La salida de ambas demostraciones queda guardada en
`evidencias\demo_defectos.txt`.

## 8. Paso 6 (opcional) — App Android

Solo si quieres ejecutar el plan CP-MOV. La app no forma parte de las figuras obligatorias del reporte.

1. Enciende el backend: en `horisoft-proyecto\backend-node` ejecuta `npm start`.
2. Abre la carpeta `horisoft-proyecto\app-movil` en **Android Studio**, espera el *Gradle Sync* y ejecuta en un emulador (Pixel 5, API 30).
3. Usuarios: `juan.perez@horisoft.com` / `juan123` (Residente) y `admin@horisoft.com` / `admin123` (Administrador).

| Caso | Pasos | Resultado esperado |
|---|---|---|
| CP-MOV-01 | Login con Juan Pérez | Home con «Rol: Residente» y botón «Mis reservas» |
| CP-MOV-02 | Login con admin | Home sin botón «Mis reservas» |
| CP-MOV-03 | Contraseña incorrecta | «Correo o contraseña incorrectos» |
| CP-MOV-04 | Campos vacíos | «Ingresa tu correo y tu contraseña» |
| CP-MOV-05 | Backend apagado e intentar login | Mensaje de falta de conexión |
| CP-MOV-06 | Iniciar sesión, cerrar la app y abrirla | Entra directo al Home |
| CP-MOV-07 | Abrir «Zonas comunes» | 3 zonas; la Cancha aparece «No disponible» |
| CP-MOV-08 | Juan reserva la Piscina para una fecha futura | «Reserva creada correctamente» |
| CP-MOV-09 | Juan repite el mismo horario | Mensaje de cruce de horario |
| CP-MOV-10 | «Mis reservas» y cancelar la reserva | El estado pasa a «Cancelada» |
| CP-MOV-11 | Admin abre Zonas comunes | Botones «Solo para residentes» deshabilitados |
| CP-MOV-12 | Con `JWT_EXPIRES_IN=10s` en `.env`, esperar y abrir Zonas | Aviso de sesión vencida y vuelve al Login |

---

## 9. Qué enviarme

Guarda cada captura con este nombre y envíamelas en el chat:

| Archivo | Contenido |
|---|---|
| `fig1_django_pruebas.png` | `Ran 40 tests ... OK` |
| `fig2_express_jwt.png` | Las 5 ejecuciones `pruebas-jwt*.js` (una o varias capturas) |
| `fig3_express_manuales.png` | `pruebas-manuales.js` |
| `fig4_cruce_horario.png` | Error de cruce de horario como Ana |
| `fig5_zona_mantenimiento.png` | Error de zona en mantenimiento |
| `fig6_acceso_denegado.png` | Página 403 |
| `fig7_reservas_ana.png` | Lista de reservas de Ana |
| `fig8_plan_manual.png` | Tabla CP-01 a CP-09 llena |

Con eso actualizo el reporte y lo dejamos listo para entregar. También puedes pasarme el contenido de la
carpeta `evidencias\`.

## 10. Problemas frecuentes

| Qué ves | Causa y solución |
|---|---|
| `No hay nada escuchando en 127.0.0.1:3306` o `error 2003` | MySQL está apagado. En Laragon presiona **Start All**. Si usa otro puerto, cámbialo en `horisoft-proyecto\horisoft\settings.py` (`PORT`). Para ver el puerto: `netstat -ano \| findstr :3306` |
| `Access denied for user 'root'` | La contraseña de MySQL no está vacía. Cámbiala en `DATABASES` de `settings.py` |
| `'python' no se reconoce` | Reinstala Python marcando **Add python.exe to PATH** |
| `Django 6.x instalado, pero el proyecto usa 5.2.18` | Estás usando otro Python. Ejecuta `1_VERIFICAR_ENTORNO.bat`, que crea el `.venv` |
| `Error: That port is already in use` (8000) | Cierra el servidor anterior, o ejecuta `python manage.py runserver 8001` |
| Las pruebas de Express fallan con `JWT_SECRET` | Falta el `.env`: el paso 3 lo crea; si no, copia `.env.example` como `.env` |
| `npm install` muestra 3 vulnerabilidades | Son de `nodemon`, una herramienta de desarrollo. **No uses `npm audit fix --force`** |
| Caracteres raros (`Î£`, `â`) en la terminal | Usa **Windows Terminal** o escribe `chcp 65001` |
| La ventana del `.bat` se cierra sola | Abre `cmd` en la carpeta del kit y escribe el nombre del archivo; así verás el error |
| Node muestra `Assertion failed ... win\async.c` | Estaba corregido en este kit. Si lo ves, dime tu versión (`node --version`) |

Si algo no se resuelve: copia **todo** el texto de la terminal (clic derecho, seleccionar todo, copiar) y pégalo en el chat.

## 11. Cuando termines: subirlo a GitHub (opcional)

Copia el contenido de `horisoft-proyecto` sobre tu repositorio y, desde su carpeta:

```
git status
git add .
git commit -m "feat: usuarios, reservas, pruebas CP-01 a CP-32 y correcciones de las suites"
git push
```

El `.gitignore` ya excluye `.venv`, `.env` y `node_modules`. Revisa con `git status` que **no** aparezca
ningún `.env` antes de hacer el `commit`.
