# HORISOFT

**Backend unificado con arquitectura limpia (Separación de Responsabilidades)**
Node.js + Express + JavaScript · Todos los módulos corriendo en un solo servidor, puerto **3000**.

## 1. Arquitectura

Cada capa tiene un único rol:

| Capa | Rol único |
|------|-----------|
| **server.js** | Punto de entrada dedicado: arranca el servidor HTTP (`app.listen`) a partir de la app ya configurada. No define rutas ni middlewares. |
| **app.js** | Configura Express: middlewares, monta las rutas y el manejo de errores. No sabe en qué puerto corre ni cómo se arranca; solo exporta la app configurada. |
| **Routes** | Recibe la petición HTTP y la delega al controlador. |
| **Controller** | Gestiona `req`/`res` y códigos de estado. No aplica lógica de negocio. |
| **Service** | Contiene toda la lógica de negocio y el acceso a los datos (arrays en memoria). |
| **Model** | Define la forma de cada entidad del dominio. |
| **Data** | Arreglos en memoria que actúan como "base de datos". |

> Esta separación entre `app.js` y `server.js` responde a una recomendación de
> retroalimentación: sobrecargar un único archivo con la configuración de
> Express **y** el arranque del servidor es una mala práctica de
> arquitectura. Ahora `app.js` es reutilizable (por ejemplo, en pruebas
> automatizadas que importen la app sin levantar un puerto real), y
> `server.js` es el único responsable de decidir cómo y cuándo se inicia
> el servicio.

## 2. Estructura del proyecto

```
horisoft/
├── server.js       (arranca el servidor)
├── app.js          (configura Express: middlewares, rutas, errores)
├── package.json
├── models/         (14 clases de dominio)
├── data/           (14 fuentes de datos en memoria)
├── services/       (14 servicios con la lógica de negocio)
├── controllers/    (14 controladores)
└── routes/         (15 archivos de rutas)
```

## 3. Instalación y ejecución

```bash
cd horisoft
npm install
npm run dev      # con nodemon (ejecuta server.js)
# o
npm start        # ejecuta server.js directamente
npm test         # suites de integración JWT y módulos
```

Verás en la consola: `HORISOFT escuchando en http://localhost:3000`

## 4. Módulos y endpoints (todos en el puerto 3000)

| Módulo | Ruta base | Reglas de negocio clave |
|--------|-----------|---------------------------|
| Zonas Comunes | `/zonas-comunes` | Estados válidos: Disponible / Mantenimiento / Inactiva |
| Reservas | `/reservas` | Sin cruces de horario; zona debe estar Disponible; fecha no pasada |
| Vigilantes | `/vigilantes` | Documento único |
| Visitantes | `/visitantes` | Vigilante debe estar Activo; no doble ingreso activo |
| Autenticación | `/auth` (`/registro`, `/login`) | Correo único; valida credenciales y estado Activo |
| Usuarios | `/usuarios` | Roles: Administrador, Residente, Vigilante, Administrativo, Proveedor |
| PQR | `/pqr` | No se responde una PQR ya cerrada |
| Comunicaciones | `/comunicados` | Destinatario válido; no se archiva dos veces |
| Cuentas de Cobro | `/cuentas-cobro` | Valor > 0 |
| Pagos | `/pagos` | No excede saldo pendiente; auto-marca "Pagada" |
| Proveedores | `/proveedores` | NIT único |
| Inventario | `/inventario` | Cantidad no negativa |
| Vehículos | `/vehiculos` | Placa única |
| Documentos | `/documentos` | Tipo válido (Reglamento/Acta/Circular/Otro) |
| Configuración | `/configuracion` | Clave única al crear |

Cada ruta soporta las operaciones CRUD documentadas en los proyectos
anteriores (ver ejemplos de curl en la sección 5).

## 5. Ejemplos de prueba (curl)

```bash
# Ver el listado de todos los módulos disponibles
curl http://localhost:3000/

# Zonas comunes y reservas
curl http://localhost:3000/zonas-comunes
curl -X POST http://localhost:3000/reservas -H "Content-Type: application/json" \
  -d '{"id_zona":1,"id_residencia":101,"fecha":"2026-08-01","hora_inicio":"14:00","hora_fin":"18:00"}'

# Seguridad
curl -X POST http://localhost:3000/visitantes -H "Content-Type: application/json" \
  -d '{"nombre":"Ana Gomez","documento":"111222333","id_residencia":5,"id_vigilante":1}'

# Autenticación (credenciales demo solo con NODE_ENV=development o test)
curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
  -d '{"correo":"admin@horisoft.com","password":"admin123"}'

# Financiera
curl -X POST http://localhost:3000/pagos -H "Content-Type: application/json" \
  -d '{"id_cuenta":1,"valor_pagado":50000,"metodo_pago":"Efectivo"}'
```

## 6. Verificación realizada

Se probó que los 14 servicios cargan juntos sin conflictos de nombres ni de
rutas relativas (`require`), y se ejecutaron pruebas cruzadas exitosas:
crear una reserva (depende de `zonasComunes.service`), registrar un pago
(depende de `cuentasCobro.service`) y registrar el ingreso de un visitante
(depende de `vigilantes.service`) — todo dentro del mismo servidor y puerto.

## 7. Alcance y limitaciones

Este directorio es un prototipo didáctico; sus arreglos en memoria no son
persistentes ni sustituyen el backend oficial Django + MySQL. No conectarlo a
datos reales ni usarlo como servicio de producción. Las contraseñas de las
cuentas de demostración solo se cargan cuando `NODE_ENV` es `development` o `test`.

## 8. Módulo de Autenticación con JWT

### 8.1 Estructura del proyecto (módulo de autenticación)

```
horisoft/
├── .env                        (JWT_SECRET, JWT_EXPIRES_IN, PORT — no versionar)
├── .env.example                (plantilla sin valores reales, sí se versiona)
├── app.js                       (carga dotenv y monta las rutas)
├── controllers/
│   └── authController.js        (login, registro, perfil)
├── services/
│   └── authService.js           (reglas de negocio + generación del JWT)
├── middlewares/
│   └── authMiddleware.js         (verificarToken: valida el header Authorization)
├── routes/
│   ├── authRoutes.js             (/auth/registro, /auth/login, /auth/perfil)
│   └── usuarios.routes.js        (ruta protegida de ejemplo: /usuarios)
├── models/
│   └── usuario.model.js
├── data/
│   └── usuarios.js
└── pruebas-jwt.js                (pruebas end-to-end del flujo completo)
```

### 8.2 Servicio de autenticación (`services/authService.js`)

- `login(correo, password)`: valida el hash bcrypt y el estado `Activo`; si
  son correctas, firma un JWT con `jwt.sign()` usando `JWT_SECRET` (desde
  `.env`) y lo devuelve junto con los datos del usuario (sin credenciales).
- Las claves se almacenan en `passwordHash` con `bcryptjs` (factor 12).
  Ninguna respuesta de usuario incluye `password` ni `passwordHash`.
- `generarToken(usuario)`: encapsula la firma del token. El payload incluye
  solo lo necesario para autorizar (`id_usuario`, `correo`, `rol`) — nunca
  el password.
- El servicio falla rápido (`throw`) al arrancar si falta `JWT_SECRET` en
  el entorno, para detectar el error de configuración de inmediato en vez
  de fallar más adelante con un mensaje críptico.

### 8.3 Rutas de autenticación (`routes/authRoutes.js`)

| Método | Ruta | Protegida | Descripción |
|--------|------|-----------|-------------|
| POST | `/auth/registro` | Sí, Administrador | Crea un usuario nuevo |
| POST | `/auth/login` | No | Valida credenciales y devuelve el Token JWT |
| GET | `/auth/perfil` | Sí | Ruta de prueba: devuelve el payload del token decodificado |
| GET | `/usuarios` | Sí, Administrador | Consulta y gestiona usuarios |

### 8.4 Middleware de autenticación (`middlewares/authMiddleware.js`)

Valida el header `Authorization: Bearer <token>` con `jwt.verify()`:

- Sin header → **401** `token no proporcionado`.
- Header sin el esquema `Bearer` → **401** `formato de token inválido`.
- Token mal firmado, corrupto o expirado → **403** `token inválido o expirado`.
- Token válido → agrega `req.usuario` (payload decodificado) y llama a `next()`.

Se aplica como segundo argumento de cualquier ruta que se quiera proteger:

```js
router.get("/", verificarToken, controller.listar);
```

### 8.5 Seguridad y permisos

- **Separación de responsabilidades**: el middleware solo valida el token;
  el service solo firma/verifica reglas de negocio; el controller solo
  traduce a `req`/`res`.
- **Secretos fuera del código**: `JWT_SECRET` vive en `.env` (no
  versionado); se entrega `.env.example` como plantilla.
- **Mensajes de error sin filtrar información sensible**: "Credenciales
  inválidas" no revela si el correo existe o no, para evitar enumeración
  de cuentas.
- **Hash de contraseñas**: `bcryptjs` con factor 12; solo se conserva el hash
  y se verifica mediante comparación bcrypt.
- **Sin cuentas demo fuera de desarrollo/pruebas**: salvo que
  `NODE_ENV=development` o `NODE_ENV=test`, el arranque exige
  `HORISOFT_ADMIN_EMAIL` y `HORISOFT_ADMIN_PASSWORD` (mínimo 12 caracteres)
  para crear el administrador inicial. No hay fallback a claves conocidas.
- **Roles granulares**: `/auth/registro` y `/usuarios` son exclusivos de
  Administrador; Administrativo gestiona operaciones permitidas por módulo;
  Residente puede crear reservas y PQR; Vigilante puede registrar ingreso y
  salida de visitantes; Proveedor no puede escribir. Las lecturas de los
  módulos de este prototipo siguen públicas, salvo los datos de `/usuarios`.
- **El password y su hash nunca se exponen** en login, registro o listados.
- **Expiración del token**: `JWT_EXPIRES_IN` (1h por defecto) limita la
  ventana de uso de un token robado o filtrado.
- **Cierre ordenado**: `server.js` escucha SIGINT/SIGTERM, deja de aceptar
  conexiones y cierra el servidor sin `process.exit()`.

### 8.6 Cómo probarlo

```bash
npm install
npm run dev

# Ejecutar todas las pruebas de integración
npm test

# Login manual de demostración (solo fuera de producción)
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"admin@horisoft.com","password":"admin123"}'

# Ruta protegida SIN token -> 401
curl -i http://localhost:3000/usuarios

# Ruta protegida CON token válido -> 200
curl http://localhost:3000/usuarios -H "Authorization: Bearer <token_obtenido_en_login>"
```

## 9. Zonas Comunes y Reservas — protegidas con JWT

Siguiendo el mismo `authMiddleware.js`, las operaciones de escritura de estos
dos módulos ahora exigen un Token JWT válido; la lectura permanece pública:

| Método y ruta | Permiso |
|---|---|---|
| GET /zonas-comunes y GET /reservas | Público | Lectura del prototipo |
| POST /zonas-comunes | Administrador, Administrativo | Gestión de catálogo |
| POST /reservas | Administrador, Administrativo, Residente | Crear reserva |
| PUT /reservas/:id/estado | Administrador, Administrativo | Gestionar estado |
| DELETE /reservas/:id | Administrador | Eliminar |

```bash
node pruebas-jwt-modulos.js
```

Última ejecución: 8 pruebas correctas, 0 fallidas.

## 11. PQR — protegido con JWT

Mismo criterio: lectura pública, escritura protegida.

| Método y ruta | Permiso |
|---|---|---|
| GET /pqr | Público | Lectura del prototipo |
| POST /pqr | Administrador, Administrativo, Residente | Radicar PQR |
| PUT /pqr/:id/respuesta, PUT /pqr/:id/estado | Administrador, Administrativo | Gestionar PQR |
| DELETE /pqr/:id | Administrador | Eliminar |

```bash
node pruebas-jwt-pqr.js
```

Resultado esperado: 6 pruebas correctas, 0 fallidas (CP-PQR-01 a CP-PQR-06).

## 12. Roles por módulo

Las operaciones de escritura exigen JWT y autorización por rol. Las rutas GET
del prototipo son públicas, excepto `/usuarios`; `HEAD` hereda el permiso de
GET y no permite eludir la protección.

| Módulo | Permisos de escritura |
|---|---|
| Usuarios y registro | Administrador |
| Zonas, vigilantes, vehículos, proveedores, inventario, cuentas, pagos, documentos, comunicados | Administrador y Administrativo (eliminación: Administrador) |
| Reservas y PQR | Residente puede crear; Administrador/Administrativo gestionan |
| Visitantes | Vigilante puede registrar ingreso/salida; Administrador/Administrativo también |
| Configuración | Administrador |
| Proveedor | Sin escrituras |

```bash
npm test
```

### Resumen de todas las pruebas del proyecto

| Archivo | Casos | Cubre |
|---|---|---|
| pruebas-jwt.js | 22 | Autenticación, roles, hashes y arranque de producción |
| pruebas-jwt-modulos.js | 8 | Zonas Comunes + Reservas |
| pruebas-jwt-pqr.js | 6 | PQR |
| pruebas-jwt-residencia.js | 7 | Residencia y reservas |
| pruebas-jwt-resto.js | 29 | Financiera, Comunicaciones, Documentos, Seguridad, Inventario, Proveedores, Configuración |
| pruebas-manuales.js | 33 | Reglas de negocio de los 14 módulos (sin JWT) |
| **Total `npm test`** | **72** | **Integración JWT, módulos y permisos** |

La cantidad de aserciones se debe contrastar con la salida real de `npm test`;
las pruebas manuales no forman parte del total automatizado.

## 13. Auditoría de dependencias y límite de producción

La última auditoría reportó **0 vulnerabilidades en dependencias de
producción** (`npm audit --omit=dev`). La auditoría completa aún informa dos
advisories moderados de `minimatch`, transitivo de `nodemon`; npm propone como
arreglo forzado instalar `nodemon@1.0.2`, un downgrade incompatible, por lo
que no se aplicó. Revisar la actualización de esa cadena antes de usar
`npm run dev`. Este backend conserva datos en memoria y no está aprobado para
despliegue productivo.

## 14. Control de versiones

Este proyecto se entrega versionado con Git (no como un .zip suelto). El
historial de commits documenta la construcción por etapas: estructura base →
modelos y datos → controladores/servicios → rutas → módulo de autenticación →
middleware y protección de Usuarios → pruebas → protección de Zonas Comunes
y Reservas.

Para conectarlo a un repositorio remoto en GitHub:

```bash
git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
git push -u origin main
```
