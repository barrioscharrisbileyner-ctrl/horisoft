# Evidencias técnicas para entrega SENA

Este documento describe cómo producir evidencias reproducibles sin incluir
credenciales, datos personales ni una copia de la base real.

## Evidencias de implementación

1. **Arquitectura:** explicar las apps y responsabilidades usando
   [arquitectura.md](arquitectura.md).
2. **Modelo de datos:** generar un diagrama o exportación del esquema a partir
   de migraciones/modelos; sustituir nombres, documentos y correos reales por
   datos ficticios antes de compartirlo.
3. **Reglas de negocio:** mostrar validaciones de reservas, PQR, pagos,
   proveedores y cargas documentales, junto con sus pruebas automatizadas.
4. **API:** guardar el JSON de `GET /api/v1/schema/` y documentar un ejemplo de
   login con tokens ficticios o redactados.
5. **Seguridad:** presentar controles de autenticación, permisos, throttling,
   auditoría y descarga privada descritos en [seguridad.md](seguridad.md).
6. **Despliegue:** capturar el estado de Docker Compose y Nginx solo cuando
   Docker esté instalado y configurado; no mostrar el contenido de `.env`.
7. **CI:** mostrar la ejecución de GitHub Actions y conservar el reporte de
   cobertura; no adjuntar logs que incluyan variables de entorno.

## Comandos de validación

Ejecuta desde la carpeta que contiene `manage.py`:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
coverage run manage.py test
coverage report --fail-under=55
```

Para validar la configuración de producción, define temporalmente variables
de entorno seguras en la sesión local y ejecuta:

```powershell
python manage.py check --deploy --fail-level WARNING
```

No uses capturas de la consola si muestran claves, URLs privadas o registros de
personas. Las evidencias deben provenir de una base de pruebas con datos
ficticios.

## Resultados de validación de esta iteración

| Componente | Evidencia ejecutada | Resultado | Estado / pendiente |
|---|---|---|---|
| Django | `.venv\Scripts\python.exe manage.py check` | Sin problemas | Cumple |
| Django | `makemigrations --check --dry-run` | No hay cambios de migración pendientes | Cumple |
| Django | `.venv\Scripts\python.exe manage.py test` | 108 pruebas, 0 fallidas | Cumple |
| Laragon/MySQL | `migrate --plan` sobre la base configurada | No hay migraciones pendientes | Cumple |
| MySQL vacío | Crear base temporal aislada, ejecutar todas las migraciones, contar tablas y eliminarla | 36 tablas creadas; migraciones completas; base temporal eliminada | Cumple |
| Comandos de instalación | `crear_administrador`, `crear_datos_demo` y `runserver` en la base temporal | Comandos terminaron correctamente; `/api/v1/health/` respondió HTTP 200; base eliminada | Cumple |
| Laragon/MySQL real | Migraciones aplicadas en fases anteriores tras respaldos previos | Completado sin modificar datos demo | Cumple |
| Express | `npm test` | 72 aserciones, 0 fallidas | Cumple |
| Express | `npm audit --omit=dev` | 0 vulnerabilidades de producción | Cumple |
| Express | `npm audit` | 2 advisories moderados en `minimatch` transitivo de `nodemon`; `--force` propone un downgrade incompatible | Pendiente documentado |
| Android | `gradlew.bat assembleDebug` con SDK configurado | Build exitoso; APK debug generado | Cumple; no verificado visualmente |
| Docker | `docker compose config --quiet` con valores temporales de validación | Configuración válida | Cumple |
| Docker | `docker compose up --build` | No ejecutado: Docker Engine no está disponible | Pendiente del aprendiz |
| Documentación | Generación de manuales con `docx`; revisión de ZIP/XML | Dos archivos Word válidos | Cumple; agregar capturas reales solo si se obtienen |
| Módulos Django | Paginación de PQR, comunicaciones, documentos, proveedores, configuración e inventario; vistas y plantillas extienden la base compartida; confirmaciones en las acciones destructivas implementadas | 42 pruebas focalizadas y 108 pruebas en la suite completa; `manage.py check` sin problemas | Cumple en pruebas automatizadas; revisión manual CRUD por rol aún pendiente |

Las migraciones reales se ejecutaron después de copias de seguridad guardadas
fuera del repositorio. No se incluyen dumps ni se agregan datos de demostración
a la base poblada.
