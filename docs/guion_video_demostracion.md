# Guion de video de demostración — Horisoft (6 minutos)

> Graba únicamente en una base de pruebas con datos ficticios. Inserta
> capturas reales del entorno que uses; no muestres `.env`, contraseñas,
> tokens, correos reales ni datos de residentes.

| Tiempo | Escena y narración | Acción en pantalla |
|---|---|---|
| 0:00–0:30 | “Horisoft es un sistema de administración de propiedad horizontal. Django + MySQL es el backend oficial; Android consume la API JWT.” | Mostrar portada y estructura general, sin abrir archivos con secretos. |
| 0:30–1:10 | “El acceso se controla por rol y copropiedad. Cada usuario ve únicamente las funciones autorizadas.” | Abrir `/usuarios/login/` e iniciar con una cuenta ficticia. |
| 1:10–2:00 | “El Administrador gestiona usuarios, permisos y operación; el panel concentra indicadores.” | Mostrar el panel Administrativo y los accesos del Administrador. |
| 2:00–2:50 | “Un residente consulta zonas comunes y solicita una reserva. El backend valida horario, disponibilidad y residencia.” | Cerrar sesión; entrar como residente de prueba; abrir zonas y completar una reserva ficticia. |
| 2:50–3:35 | “El residente puede revisar y cancelar sus reservas, y radicar una PQR sin modificar su estado administrativo.” | Mostrar Mis reservas y el flujo PQR con datos de prueba. |
| 3:35–4:20 | “Financiera registra cuentas, pagos, multas y convenios con controles de saldo. Seguridad gestiona visitantes, cámaras y vehículos.” | Mostrar listados y una validación de prueba; evitar revelar información real. |
| 4:20–5:00 | “El Vigilante tiene permisos de consulta y registro de visitantes, sin acceso a las funciones de administración financiera.” | Iniciar sesión con cuenta ficticia de Vigilante y mostrar las opciones disponibles. |
| 5:00–5:40 | “La API documentada usa JWT, paginación y permisos; la app Android conserva tokens y renueva el acceso.” | Mostrar `docs/api-v1.md` y, si el emulador está disponible, el login y zonas de la app. |
| 5:40–6:00 | “La compilación del APK y las pruebas automatizadas se validan por separado. Docker requiere que el motor esté iniciado para probar contenedores.” | Mostrar resultados de pruebas redactados y cerrar con limitaciones verificadas. |

## Preparación antes de grabar

1. Levanta una base de pruebas, aplica migraciones y crea cuentas ficticias
   para los roles que vayas a demostrar.
2. No ejecutes `crear_datos_demo` ni acciones de escritura en la base real.
3. Prueba los recorridos y verifica qué menús están disponibles en cada rol.
4. Comprueba enfoque, resolución y legibilidad; oculta nombres y datos
   identificables.
5. Si Android o Docker no están disponibles durante la grabación, dilo
   explícitamente y muestra solo la verificación que sí se ejecutó.
