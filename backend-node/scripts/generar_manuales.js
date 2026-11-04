const fs = require("node:fs");
const path = require("node:path");
const {
    Document,
    HeadingLevel,
    Packer,
    Paragraph,
    Table,
    TableCell,
    TableRow,
    TextRun,
    WidthType,
} = require("docx");

const raiz = path.resolve(__dirname, "../..");
const carpetaDocs = path.join(raiz, "docs");

function parrafo(texto) {
    return new Paragraph({
        children: [new TextRun({ text: texto })],
        spacing: { after: 120 },
    });
}

function titulo(texto) {
    return new Paragraph({
        text: texto,
        heading: HeadingLevel.TITLE,
        spacing: { after: 260 },
    });
}

function encabezado(texto, nivel = HeadingLevel.HEADING_1) {
    return new Paragraph({ text: texto, heading: nivel, keepNext: true });
}

function viñeta(texto) {
    return new Paragraph({
        text: texto,
        bullet: { indent: 360 },
        spacing: { after: 80 },
    });
}

function tabla(encabezados, filas) {
    const crearFila = (valores, esEncabezado = false) => new TableRow({
        tableHeader: esEncabezado,
        children: valores.map(valor => new TableCell({
            children: [esEncabezado
                ? new Paragraph({ children: [new TextRun({ text: valor, bold: true, color: "FFFFFF" })] })
                : parrafo(valor)],
            ...(esEncabezado ? { shading: { fill: "1E293B" } } : {}),
        })),
    });

    return new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [crearFila(encabezados, true), ...filas.map(fila => crearFila(fila))],
    });
}

function marcadorCaptura(texto) {
    return new Paragraph({
        children: [new TextRun({ text: `[INSERTAR CAPTURA: ${texto}]`, italics: true, color: "64748B" })],
        spacing: { before: 120, after: 220 },
    });
}

function documento(tituloDocumento, contenido) {
    return new Document({
        creator: "Horisoft",
        title: tituloDocumento,
        subject: "Documentación del sistema Horisoft",
        description: "Manual generado desde la documentación y el código del proyecto.",
        styles: {
            default: {
                document: {
                    run: { font: "Arial", size: 22, color: "1F2937" },
                    paragraph: { spacing: { after: 100 } },
                },
            },
            title: {
                run: { font: "Arial", size: 36, bold: true, color: "1E293B" },
                paragraph: { spacing: { after: 240 } },
            },
            heading1: {
                run: { font: "Arial", size: 30, bold: true, color: "1E293B" },
                paragraph: { spacing: { before: 240, after: 120 } },
            },
            heading2: {
                run: { font: "Arial", size: 25, bold: true, color: "3B82F6" },
                paragraph: { spacing: { before: 180, after: 100 } },
            },
        },
        sections: [{
            properties: {
                page: { margin: { top: 900, bottom: 900, left: 1000, right: 1000 } },
            },
            children: contenido,
        }],
    });
}

async function guardar(nombre, tituloDocumento, contenido) {
    const buffer = await Packer.toBuffer(documento(tituloDocumento, contenido));
    fs.writeFileSync(path.join(carpetaDocs, nombre), buffer);
}

async function main() {
    fs.mkdirSync(carpetaDocs, { recursive: true });
    const fecha = new Date().toLocaleDateString("es-CO");

    const manualUsuario = [
        titulo("HORISOFT"),
        parrafo("Manual de usuario"),
        parrafo(`Sistema de administración de propiedad horizontal · Versión documental: ${fecha}`),
        parrafo("Backend oficial: Django + MySQL. Este manual no contiene credenciales ni datos personales reales."),
        encabezado("1. Objetivo y alcance"),
        parrafo("Este manual describe el acceso y las tareas habituales de los perfiles Administrador, Administrativo, Residente, Vigilante y Proveedor. Las opciones disponibles dependen del rol y de las copropiedades asignadas."),
        parrafo("La aplicación Android es una interfaz para residentes y consume la API JWT de Django. El prototipo Express no es el sistema oficial y no debe usarse con información real."),
        marcadorCaptura("pantalla de inicio de sesión con datos ficticios"),
        encabezado("2. Requisitos de acceso"),
        viñeta("Navegador actualizado y conexión al servidor Horisoft."),
        viñeta("Una cuenta habilitada por el Administrador. No comparta contraseñas ni tokens."),
        viñeta("Para la app Android: un dispositivo o emulador con acceso al backend Django."),
        encabezado("3. Iniciar y cerrar sesión"),
        parrafo("1. Abra la dirección entregada por el responsable del sistema y visite /usuarios/login/."),
        parrafo("2. Ingrese el correo y la contraseña de su cuenta. Si los datos son correctos, el sistema abrirá el panel correspondiente al rol."),
        parrafo("3. Para salir, use la opción Cerrar sesión del menú. En un dispositivo compartido, cierre siempre la sesión."),
        parrafo("Si la cuenta está inactiva, no tiene perfil o la contraseña no es válida, contacte al Administrador. No solicite ni envíe contraseñas por capturas."),
        encabezado("4. Tareas por rol"),
        encabezado("4.1 Administrador", HeadingLevel.HEADING_2),
        viñeta("Crear y administrar cuentas, asignar roles y permisos por copropiedad."),
        viñeta("Gestionar personas, unidades, residencias, zonas comunes y reservas."),
        viñeta("Administrar PQR, comunicaciones, documentos, seguridad, inventario, proveedores, parámetros y cartera."),
        viñeta("Consultar el panel Administrativo, realizar respaldos y coordinar cambios de producción."),
        marcadorCaptura("panel administrativo usando datos ficticios"),
        encabezado("4.2 Administrativo", HeadingLevel.HEADING_2),
        viñeta("Usar el panel de gestión y atender las operaciones habilitadas por su rol."),
        viñeta("Crear/editar información operativa, gestionar PQR y reservas y consultar cartera según la matriz de permisos."),
        viñeta("Las acciones de eliminación o configuración reservadas al Administrador no aparecerán habilitadas."),
        encabezado("4.3 Residente", HeadingLevel.HEADING_2),
        viñeta("Consultar sus zonas y reservas; crear una reserva indicando zona, residencia, fecha y horario disponibles."),
        viñeta("Cancelar una reserva propia cuando su estado lo permita."),
        viñeta("Radicar y consultar PQR propias; consultar su información financiera y comunicados disponibles."),
        viñeta("Registrar o actualizar vehículos propios si el formulario está habilitado para su cuenta."),
        marcadorCaptura("listado de reservas propias o formulario con información ficticia"),
        encabezado("4.4 Vigilante", HeadingLevel.HEADING_2),
        viñeta("Consultar la información de residentes, unidades, reservas y seguridad autorizada."),
        viñeta("Registrar el ingreso y la salida de visitantes de acuerdo con los controles del sistema."),
        viñeta("No puede gestionar usuarios, modificar cartera ni administrar catálogos restringidos."),
        marcadorCaptura("registro de visitante con identidad ficticia"),
        encabezado("4.5 Proveedor", HeadingLevel.HEADING_2),
        viñeta("Su acceso depende de la asignación vigente; no dispone de acciones administrativas de escritura."),
        encabezado("5. Uso desde Android"),
        parrafo("La app permite iniciar sesión, ver las zonas comunes, solicitar una reserva y revisar/cancelar reservas propias. El cliente conserva tokens de acceso y renovación; si el acceso expira, intenta renovarlo una vez. Un error 403 indica falta de permiso; un 401 persistente requiere iniciar sesión de nuevo."),
        parrafo("En caso de error de red, confirme que el servidor esté activo y que la dirección del backend sea accesible desde el dispositivo. La compilación APK no sustituye la verificación visual en un dispositivo real."),
        marcadorCaptura("pantalla de zonas comunes y confirmación de reserva"),
        encabezado("6. Buenas prácticas y solución de problemas"),
        tabla(
            ["Situación", "Qué hacer"],
            [
                ["No puedo iniciar sesión", "Verifique el correo; si persiste, contacte al Administrador para revisar estado y restablecer la cuenta."],
                ["No aparece una copropiedad o registro", "Solicite al Administrador que revise su rol, residencia y accesos asignados."],
                ["La reserva no se guarda", "Revise fecha, hora, disponibilidad y mensajes de validación; no reenvíe varias veces una solicitud pendiente."],
                ["La app indica sesión vencida", "Vuelva a iniciar sesión; el refresh también puede haber expirado."],
                ["El servidor no responde", "Notifique al responsable técnico; no cambie las credenciales ni configuración de producción."],
            ]
        ),
        parrafo("Al reportar un problema, describa la pantalla, la hora aproximada y el mensaje; oculte nombres, documentos, correos, tokens y datos financieros."),
        encabezado("7. Marcadores de evidencia"),
        parrafo("Los marcadores entre corchetes son espacios reservados para capturas suministradas por el aprendiz. No se generaron capturas ficticias ni se incluyeron registros reales."),
    ];

    const entidades = [
        ["Estructura y acceso", "PropiedadHorizontal, AccesoPropiedad, Persona, UnidadResidencial, Residencia, PerfilUsuario"],
        ["Reservas", "ZonaComun, Reserva"],
        ["Atención", "Pqr, Comunicado, Documento"],
        ["Finanzas", "CuentaCobro, Pago, Multa, ConvenioPago"],
        ["Seguridad", "Vigilante, Visitante, Camara, Vehiculo"],
        ["Operación", "ItemInventario, Proveedor, ParametroConfiguracion"],
    ];

    const manualTecnico = [
        titulo("HORISOFT"),
        parrafo("Manual técnico"),
        parrafo(`Arquitectura, instalación, operación y mantenimiento · ${fecha}`),
        parrafo("Este documento describe únicamente decisiones y verificaciones disponibles en el proyecto; no incluye secretos ni datos reales."),
        encabezado("1. Arquitectura y alcance"),
        parrafo("El backend oficial es Django 5.2 con Django REST Framework y SimpleJWT. MySQL es el motor objetivo; PyMySQL permite su uso en Windows/Laragon. Gunicorn sirve WSGI, WhiteNoise maneja estáticos, y Docker Compose define MySQL, Redis, Django y Nginx."),
        parrafo("Las reglas están separadas por aplicaciones Django. `backend-node/` es un prototipo didáctico aislado, con datos en memoria; no se debe desplegar ni integrar a datos reales. La app Android (Java) consume `/api/v1/` de Django."),
        tabla(["Capa", "Responsabilidad"], [
            ["Modelos y formularios", "Integridad, reglas de dominio y validación de entradas."],
            ["Vistas web", "Interfaz de sesión, autorización por rol y copropiedad."],
            ["API v1", "JWT, serializadores, permisos DRF, paginación y respuestas JSON."],
            ["Auditoría", "Actor, método, ruta y código de respuesta en escrituras; no almacena cuerpos."],
            ["Android", "Login, refresh, zonas y ciclo de reserva a través de la API."],
        ]),
        encabezado("2. Componentes Django"),
        tabla(["Aplicación", "Responsabilidad"], [
            ["residentes", "Propiedades, personas, unidades, residencias y accesos."],
            ["usuarios", "Perfiles, roles, permisos, panel y comandos de administración."],
            ["reservas", "Zonas comunes y reservas."],
            ["pqrs / financiera", "Atención, cuentas, pagos, multas y convenios."],
            ["comunicaciones / documental", "Comunicados y documentos privados."],
            ["seguridad", "Vigilantes, visitantes, cámaras y vehículos."],
            ["inventario / proveedores / configuracion", "Catálogos operativos por copropiedad."],
            ["api_v1 / auditoria", "API móvil y trazabilidad de escrituras."],
        ]),
        encabezado("3. Modelo de datos conceptual"),
        parrafo("El código declara 22 modelos de dominio. El esquema definitivo se obtiene de las migraciones; las relaciones siguientes son una guía conceptual y deben contrastarse con el ER generado antes de una modificación de base de datos."),
        tabla(["Área", "Modelos"], entidades),
        viñeta("PropiedadHorizontal delimita unidades, zonas y catálogos; AccesoPropiedad asigna acceso explícito a usuarios administrativos."),
        viñeta("Persona, UnidadResidencial y Residencia representan la relación persona/unidad/rol; PerfilUsuario vincula identidad y permisos."),
        viñeta("Reserva relaciona zona común y residencia; PQR, visitante, vehículo y cartera se consultan dentro del ámbito autorizado."),
        viñeta("CuentaCobro se relaciona con pagos y convenios; multas pertenecen a una residencia. Cámara puede asociarse a una zona."),
        viñeta("Los modelos operativos restantes guardan catálogos asociados a su copropiedad según sus claves foráneas."),
        tabla(["Relación principal", "Cardinalidad conceptual"], [
            ["PropiedadHorizontal → UnidadResidencial / ZonaComun / catálogos", "1 a muchos"],
            ["Persona → Residencia ← UnidadResidencial", "1 a muchos desde persona y unidad"],
            ["Usuario → PerfilUsuario; PerfilUsuario → Persona", "uno a uno"],
            ["Usuario → AccesoPropiedad ← PropiedadHorizontal", "1 a muchos por usuario y propiedad"],
            ["ZonaComun + Residencia → Reserva", "1 a muchos desde cada entidad"],
            ["Residencia → Pqr / CuentaCobro / Multa / Vehiculo", "1 a muchos"],
            ["CuentaCobro → Pago / ConvenioPago", "1 a muchos"],
            ["Residencia + Vigilante → Visitante; ZonaComun → Camara", "1 a muchos"],
            ["Usuario autor → Comunicado / Documento responsable", "1 a muchos"],
        ]),
        parrafo("La tabla no sustituye un diagrama ER gráfico ni las cardinalidades exactas del esquema. Para la entrega visual, genere el ER desde modelos/migraciones y agregue aquí la captura validada."),
        marcadorCaptura("diagrama ER generado desde el esquema vigente, sin datos personales"),
        encabezado("4. Instalación local en Windows + Laragon"),
        parrafo("1. Inicie MySQL en Laragon. Use una base de pruebas vacía para validar una instalación; no ejecute carga demo en la base poblada real."),
        parrafo("2. Cree/active el entorno virtual y restaure dependencias:"),
        parrafo("python -m venv .venv"),
        parrafo(".venv\\Scripts\\activate"),
        parrafo("pip install -r requirements.txt"),
        parrafo("3. Copie `.env.example` a `.env` y configure DJANGO_ENV, la clave secreta, hosts y credenciales MySQL. No comparta el archivo ni lo agregue a Git."),
        parrafo("4. En una base nueva o respaldada, aplique `python manage.py migrate`. Cree el Administrador con `python manage.py crear_administrador --correo ... --nombre ...`; el comando solicita la contraseña. `crear_datos_demo` se reserva para una base aislada de pruebas."),
        parrafo("5. Ejecute `python manage.py runserver`. La administración está en `/admin/`; el login web en `/usuarios/login/`; la API en `/api/v1/`."),
        encabezado("5. Autenticación, permisos y aislamiento"),
        viñeta("Las vistas web requieren sesión y aplican `@rol_requerido` según `usuarios/permisos.py`; los usuarios no residentes requieren accesos explícitos por copropiedad."),
        viñeta("Los residentes heredan alcance de sus residencias activas. Formularios, vistas, DRF y administración filtran el mismo ámbito."),
        viñeta("JWT se emite en login; access dura 15 minutos, refresh permite renovar según la configuración. Las listas API usan paginación DRF de 20 elementos."),
        viñeta("PQR no permite que el cliente establezca respuesta/estado. Las reservas reutilizan `ReservaForm` para mantener validaciones coherentes."),
        viñeta("En producción, `DJANGO_ENV=production` exige una clave fuerte y hosts definidos; use HTTPS, cookies seguras y una cuenta MySQL de privilegios mínimos."),
        tabla(["Función", "Roles principales"], [
            ["Residentes, unidades y residencias", "Administrador y Administrativo gestionan; Vigilante consulta."],
            ["Zonas comunes y reservas", "Administrador/Administrativo gestionan; Residente usa sus reservas; Vigilante consulta."],
            ["Cuentas, pagos, multas y convenios", "Administrador/Administrativo gestionan; Residente consulta lo propio."],
            ["Seguridad y visitantes", "Administrador/Administrativo gestionan; Residente/Vigilante consultan; Vigilante registra visitantes."],
            ["Panel Administrativo", "Administrador y Administrativo."],
        ]),
        encabezado("6. API y aplicación móvil"),
        parrafo("Consultar `docs/api-v1.md` para métodos, rutas, permisos y contratos. Endpoints principales: login/refresh/me, zonas, reservas (lista, detalle, crear, cancelar), PQR, comunicados y perfil residente."),
        parrafo("El emulador Android usa `http://10.0.2.2:8000/api/v1`; para un teléfono físico configure la IP LAN en `ApiClient.BASE_URL` y habilite el host en Django."),
        parrafo("Build debug: desde `app-movil/`, definir ANDROID_HOME/ANDROID_SDK_ROOT y ejecutar `gradlew.bat assembleDebug`. APK: `app-movil/app/build/outputs/apk/debug/app-debug.apk`."),
        encabezado("7. Despliegue Docker"),
        parrafo("Compose define servicios MySQL 8.4, Redis, web y Nginx. Prepare variables distintas en `.env`; el proxy enlaza a loopback de forma predeterminada. Orden recomendado tras respaldo:"),
        parrafo("docker compose up -d db\n# espere healthcheck\ndocker compose --profile maintenance run --rm migrate\ndocker compose up --build -d web nginx"),
        parrafo("Los estáticos se recopilan durante la construcción de la imagen. El servicio web no migra al arrancar. Exponer el sistema a Internet requiere un terminador TLS confiable y configuración correcta de X-Forwarded-Proto."),
        encabezado("8. Pruebas y estado verificable"),
        viñeta("Django: `python manage.py check`, `makemigrations --check --dry-run` y `python manage.py test` (ejecutar desde el entorno virtual del proyecto)."),
        viñeta("Express: `cd backend-node; npm test`; también existe `npm audit --omit=dev` para dependencias de producción."),
        viñeta("Android: build Gradle debug; el APK compilado no implica prueba visual."),
        viñeta("Docker: `docker compose config --quiet` valida sintaxis; para probar contenedores hace falta que Docker Engine esté iniciado."),
        viñeta("Laragon: conservar respaldo antes de migrar y comprobar `showmigrations`/`migrate --plan`; no ejecutar operaciones de demo sobre datos reales."),
        parrafo("Registrar siempre la fecha, comando, resultado y evidencia. Marcar como Pendiente cualquier prueba que no se haya ejecutado en el entorno requerido."),
        encabezado("9. Respaldo, mantenimiento e incidencias"),
        parrafo("Use `scripts/backup_db.py` y `scripts/restore_db.py` siguiendo el procedimiento de confirmación documentado. Guarde respaldos fuera del repositorio con acceso restringido. No restaure un dump en la base real sin autorización y verificación de destino."),
        parrafo("Ante un error, conserve el mensaje técnico sin adjuntar `.env`, credenciales, tokens ni datos personales. Las migraciones de asignación de propiedad se detienen si la relación antigua es ambigua; resuelva la asignación antes de volver a ejecutar."),
    ];

    await guardar("Manual_Usuario_Horisoft.docx", "Manual de usuario Horisoft", manualUsuario);
    await guardar("Manual_Tecnico_Horisoft.docx", "Manual técnico Horisoft", manualTecnico);
    console.log("Manuales Word generados en docs/.");
}

main().catch(error => {
    console.error("No se pudieron generar los manuales:", error);
    process.exitCode = 1;
});
