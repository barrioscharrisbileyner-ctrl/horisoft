# Memoria del Proyecto Horisoft

## Alcance y decisiones vigentes

- **Backend oficial:** Django + Django REST Framework + MySQL.
- **Interfaz web:** Django, con sesión, CSRF, permisos por rol y aislamiento por copropiedad.
- **Aplicación móvil:** Android Java, conectada a `/api/v1/` con JWT.
- **Express:** prototipo didáctico en `backend-node/`, con datos en memoria; no se usa como backend final ni con datos reales.
- **Base de datos:** migraciones versionadas. La asignación de registros antiguos falla explícitamente cuando hay más de una copropiedad y los datos no permiten decidir la propiedad correcta.
- **Datos demo:** únicamente en una base aislada. No se cargaron datos demo en la base real poblada.

## Estado por componente

| Componente | Estado actual | Evidencia | Pendiente |
|---|---|---|---|
| Django y módulos | Implementados; aislamiento multi-copropiedad, panel Administrativo y entidades solicitadas. Listados de PQR, comunicaciones, documentos, proveedores, configuración e inventario paginados; plantillas de esos flujos comparten la base visual | `manage.py test`: 108 pruebas OK; pruebas focalizadas de módulos: 42 OK; `manage.py check` sin problemas | Completar revisión manual CRUD, confirmaciones, matriz de permisos y navegación visual por rol |
| Laragon/MySQL | Migraciones reales aplicadas tras respaldos previos | `migrate --plan`: sin operaciones pendientes. Una base temporal vacía recibió 36 tablas, migraciones y datos demo; Administrador y `runserver` funcionaron, `/api/v1/health/` respondió HTTP 200; base temporal eliminada | Repetir navegación visual sobre datos de prueba; no ejecutar datos demo en la base real |
| API v1 | JWT, paginación, permisos por rol/propiedad y endpoints para reservas, PQR, comunicados y perfil residente | Incluida en las 101 pruebas Django; documentación en `docs/api-v1.md` | Completar una matriz manual HTTP de 200/401/403/400 por endpoint y rol |
| Express | Hash bcrypt, roles granulares, restricciones de registro/usuarios, cierre SIGINT/SIGTERM y cuentas demo excluidas de entornos no dev/test | `npm test`: 72 aserciones OK; prueba de cierre ordenado; `npm audit --omit=dev`: 0 vulnerabilidades | Auditoría completa mantiene dos vulnerabilidades moderadas en `minimatch` transitivo de `nodemon`; no usar `npm audit fix --force` por el downgrade incompatible |
| App Android | Integrada con Django/JWT; APK debug compilado | `gradlew.bat assembleDebug` exitoso: `app-movil/app/build/outputs/apk/debug/app-debug.apk` | Flujo no verificado visualmente en emulador/dispositivo; PQR y Comunicados móviles no implementados |
| Docker | Compose definido y configuración sintáctica válida | `docker compose config --quiet` pasó con variables temporales | Docker Engine no estaba disponible; `docker compose up --build` no ejecutado |
| Documentación | README, API, arquitectura, seguridad, evidencias, guion de video y manuales Word | Generador Node `docx`; ambos `.docx` generados y estructura XML válida | Añadir capturas reales solo cuando el aprendiz las obtenga; completar el ER gráfico con cardinalidades revisadas |

## Pruebas registradas

| Prueba | Resultado |
|---|---|
| `python manage.py check` | Sin problemas |
| `python manage.py makemigrations --check --dry-run` | No hay cambios de migración pendientes |
| `python manage.py check --deploy --fail-level WARNING` con variables temporales seguras | Sin advertencias bloqueantes |
| `python manage.py test` (entorno virtual del proyecto) | 108 pruebas, 0 fallidas |
| Migración MySQL aislada desde cero | 36 tablas, migraciones completas; base descartable eliminada |
| `crear_administrador` + `crear_datos_demo` + `runserver` en MySQL aislado | Comandos correctos; health API HTTP 200 |
| `npm test` | 72 aserciones, 0 fallidas |
| `npm audit --omit=dev` | 0 vulnerabilidades |
| `npm audit` | 2 moderadas en dependencia de desarrollo |
| Gradle `assembleDebug` | Build exitoso; advertencias no bloqueantes de Java source/target 8 y deprecaciones Gradle |
| Docker Compose | Configuración validada; servicio no ejecutado por falta del daemon |

## Riesgos y pendientes de producción

1. Antes de desplegar, sustituir/rotar las claves y credenciales locales por
   secretos fuertes propios del entorno; no se modificó ni se publicó `.env`.
2. No exponer Express: su almacenamiento es volátil y conserva endpoints de
   lectura pública propios del prototipo.
3. Ejecutar validación visual de Android y de la interfaz web con cuentas
   ficticias de todos los roles.
4. Iniciar Docker Engine y completar el despliegue de prueba, healthchecks,
   logs y flujo TLS.
5. Resolver la cadena vulnerable de `nodemon` con una actualización
   compatible; evitar downgrade forzado.
6. Confirmar permisos y confirmaciones de eliminación de cada módulo, y
   actualizar el plan manual con los resultados realmente observados.

## Revisión CRUD y paginación

Se añadieron páginas de 20 registros en los seis listados Django que no tenían
paginación y se reutilizó el control compartido de navegación. Sus listas y
formularios ahora extienden `residentes/base.html`; las acciones destructivas
disponibles en Documental y Configuración y el archivado de Comunicaciones
solicitan confirmación en el navegador.

El ciclo de vida de entidades con trazabilidad no se debe equiparar a un CRUD
genérico: las PQR se responden y cierran, las visitas registran ingreso/salida,
y los movimientos financieros deben conservarse. Proveedores e inventario
disponen de cambios de estado; no se añadió borrado físico indiscriminado. La
revisión manual por rol y la definición de reglas de edición adicionales siguen
pendientes.

## Repositorio y commits

No se crearon commits. La carpeta de Horisoft está ubicada bajo una raíz Git
que apunta al repositorio `barrioscharrisbileyner-ctrl/mi-portafolio`, no al
repositorio de Horisoft. No se añadieron ni publicaron estos archivos para
evitar enviarlos al repositorio equivocado. Antes de versionar, abrir Horisoft
como repositorio independiente o configurar la raíz/remoto correcto y revisar
el estado completo.
