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

# Autenticación
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

## 7. Próximos pasos sugeridos

- Migrar la capa `data/` a MySQL, manteniendo intactas las demás capas.
- Agregar hashing de contraseñas (bcrypt) en Autenticación.
- Integrar `id_residencia` / `id_usuario` con el módulo real de Residentes
  y Unidades (Django) para tener un único origen de verdad.

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

- `login(correo, password)`: valida credenciales y estado `Activo`; si son
  correctas, firma un JWT con `jwt.sign()` usando `JWT_SECRET` (desde
  `.env`) y lo devuelve junto con los datos del usuario (sin password).
- `generarToken(usuario)`: encapsula la firma del token. El payload incluye
  solo lo necesario para autorizar (`id_usuario`, `correo`, `rol`) — nunca
  el password.
- El servicio falla rápido (`throw`) al arrancar si falta `JWT_SECRET` en
  el entorno, para detectar el error de configuración de inmediato en vez
  de fallar más adelante con un mensaje críptico.

### 8.3 Rutas de autenticación (`routes/authRoutes.js`)

| Método | Ruta | Protegida | Descripción |
|--------|------|-----------|-------------|
| POST | `/auth/registro` | No | Crea un usuario nuevo |
| POST | `/auth/login` | No | Valida credenciales y devuelve el Token JWT |
| GET | `/auth/perfil` | Sí | Ruta de prueba: devuelve el payload del token decodificado |
| GET | `/usuarios` | Sí | Ruta protegida "equivalente a /api/fichas" del ejercicio |

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

### 8.5 Buenas prácticas aplicadas

- **Separación de responsabilidades**: el middleware solo valida el token;
  el service solo firma/verifica reglas de negocio; el controller solo
  traduce a `req`/`res`.
- **Secretos fuera del código**: `JWT_SECRET` vive en `.env` (no
  versionado); se entrega `.env.example` como plantilla.
- **Mensajes de error sin filtrar información sensible**: "Credenciales
  inválidas" no revela si el correo existe o no, para evitar enumeración
  de cuentas.
- **El password nunca se expone**: ni en las respuestas de login/registro
  ni en el listado de usuarios (se excluye explícitamente con
  desestructuración `{ password, ...resto }`).
- **Expiración del token**: `JWT_EXPIRES_IN` (1h por defecto) limita la
  ventana de uso de un token robado o filtrado.
- **Pruebas automatizadas del flujo completo**: `pruebas-jwt.js` levanta
  el servidor real y prueba los 4 escenarios exigidos (login correcto,
  login incorrecto, ruta protegida sin token, con token inválido y con
  token válido) más casos de formato de header.

### 8.6 Cómo probarlo

```bash
npm install
npm run dev

# Pruebas automáticas del flujo JWT completo
node pruebas-jwt.js

# Login manual (equivalente a la prueba en Postman)
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

| Método y ruta | Protegida | Motivo |
|---|---|---|
| GET /zonas-comunes, GET /zonas-comunes/:id | No | Consultar disponibilidad es público |
| POST/PUT/DELETE /zonas-comunes/... | Sí | Gestión administrativa |
| GET /reservas, GET /reservas/:id | No | Consultar reservas es público |
| POST/PUT/DELETE /reservas/... | Sí | Un residente debe estar autenticado para reservar |

```bash
node pruebas-jwt-modulos.js
```

Resultado esperado: 7 pruebas correctas, 0 fallidas (CP-MOD-01 a CP-MOD-07).

## 11. PQR — protegido con JWT

Mismo criterio: lectura pública, escritura protegida.

| Método y ruta | Protegida | Motivo |
|---|---|---|
| GET /pqr, GET /pqr/:id | No | Consultar PQR es público |
| POST /pqr | Sí | El residente debe estar autenticado para reportar |
| PUT /pqr/:id/respuesta, PUT /pqr/:id/estado | Sí | Acción administrativa |
| DELETE /pqr/:id | Sí | Acción administrativa |

```bash
node pruebas-jwt-pqr.js
```

Resultado esperado: 6 pruebas correctas, 0 fallidas (CP-PQR-01 a CP-PQR-06).

## 12. Control de versiones

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


