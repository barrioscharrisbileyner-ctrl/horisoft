"""
Verifica que el equipo está listo para ejecutar Horisoft y explica qué falta.

Uso (desde la carpeta horisoft-proyecto, con el entorno virtual activado):
    python ..\\herramientas\\verificar_entorno.py --crear-bd

Revisa: Python, Django, PyMySQL, conexión a MySQL (Laragon), existencia de la base
de datos y Node.js. Termina con código 1 si algo crítico falla.
"""
import argparse
import os
import re
import shutil
import socket
import subprocess
import sys

try:  # evita errores de codificación en la consola de Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OK, MAL, AVISO = "[ OK ]", "[FALLA]", "[AVISO]"
criticos = 0


def mostrar(estado, texto):
    print(f"{estado} {texto}")


def fallo(texto, solucion):
    global criticos
    criticos += 1
    mostrar(MAL, texto)
    for linea in solucion.strip().splitlines():
        print(f"         -> {linea}")


def leer_configuracion_bd():
    """Lee HOST, PORT, NAME, USER y PASSWORD de horisoft/settings.py sin importar Django."""
    ruta = os.path.join(os.getcwd(), "horisoft", "settings.py")
    cfg = {"HOST": "127.0.0.1", "PORT": "3306", "NAME": "horisoft_db", "USER": "root", "PASSWORD": ""}
    if not os.path.exists(ruta):
        return None
    texto = open(ruta, encoding="utf-8").read()
    for clave in cfg:
        m = re.search(rf"['\"]{clave}['\"]\s*:\s*['\"]([^'\"]*)['\"]", texto)
        if m:
            cfg[clave] = m.group(1)
    return cfg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--crear-bd", action="store_true",
                        help="Crea la base de datos si no existe (utf8mb4).")
    args = parser.parse_args()

    print("=" * 60)
    print(" Verificación del entorno de Horisoft")
    print("=" * 60)

    # 1) Python
    v = sys.version_info
    if (3, 10) <= (v.major, v.minor) <= (3, 13):
        mostrar(OK, f"Python {v.major}.{v.minor}.{v.micro}")
    elif v >= (3, 13):
        fallo(f"Python {v.major}.{v.minor} aún no está validado con este kit",
              "Usa Python 3.10, 3.11, 3.12 o 3.13.")
    else:
        fallo(f"Python {v.major}.{v.minor} es muy antiguo",
              "Instala Python 3.10, 3.11, 3.12 o 3.13.")

    # 2) Entorno virtual
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        mostrar(OK, "Entorno virtual activo")
    else:
        mostrar(AVISO, "No hay entorno virtual activo (se recomienda .venv para usar Django 5.2.18)")

    # 3) Django
    try:
        import django
        if django.get_version() == "5.2.18":
            mostrar(OK, "Django 5.2.18")
        else:
            fallo(f"Django {django.get_version()} instalado, pero el proyecto usa 5.2.18",
                  "Activa el entorno virtual del proyecto y ejecuta: pip install -r requirements.txt")
    except ImportError:
        fallo("Django no está instalado", "Activa el entorno virtual y ejecuta: pip install -r requirements.txt")

    # 4) PyMySQL
    try:
        import pymysql
        mostrar(OK, f"PyMySQL {pymysql.__version__}")
    except ImportError:
        fallo("PyMySQL no está instalado", "Ejecuta: pip install -r requirements.txt")
        pymysql = None

    # 5) MySQL (Laragon)
    cfg = leer_configuracion_bd()
    if cfg is None:
        fallo("No encuentro horisoft\\settings.py",
              "Ejecuta este script desde la carpeta horisoft-proyecto (donde está manage.py).")
    else:
        destino = f"{cfg['HOST']}:{cfg['PORT']}"
        try:
            socket.create_connection((cfg["HOST"], int(cfg["PORT"])), timeout=3).close()
            mostrar(OK, f"MySQL responde en {destino}")
            puerto_abierto = True
        except OSError:
            puerto_abierto = False
            fallo(f"No hay nada escuchando en {destino}",
                  "Abre Laragon y presiona 'Start All' (o solo MySQL).\n"
                  "Si MySQL usa otro puerto, cámbialo en horisoft\\settings.py (PORT).\n"
                  "Para ver qué puerto usa:  netstat -ano | findstr :3306")

        if puerto_abierto and pymysql:
            try:
                con = pymysql.connect(host=cfg["HOST"], port=int(cfg["PORT"]),
                                      user=cfg["USER"], password=cfg["PASSWORD"], connect_timeout=5)
                mostrar(OK, f"Autenticación correcta (usuario {cfg['USER']})")
                with con.cursor() as cur:
                    cur.execute("SHOW DATABASES LIKE %s", (cfg["NAME"],))
                    existe = cur.fetchone() is not None
                    if existe:
                        mostrar(OK, f"La base de datos '{cfg['NAME']}' existe")
                    elif args.crear_bd:
                        cur.execute(f"CREATE DATABASE `{cfg['NAME']}` CHARACTER SET utf8mb4")
                        mostrar(OK, f"Base de datos '{cfg['NAME']}' creada")
                    else:
                        fallo(f"La base de datos '{cfg['NAME']}' no existe",
                              f"Créala en HeidiSQL, o ejecuta este script con --crear-bd")
                con.close()
            except Exception as e:  # noqa: BLE001
                fallo(f"No se pudo iniciar sesión en MySQL: {e}",
                      "Verifica el usuario y la contraseña de DATABASES en horisoft\\settings.py\n"
                      "(Laragon usa 'root' sin contraseña por defecto).")

    # 6) Node.js y npm (para el prototipo Express)
    node = shutil.which("node")
    if node:
        try:
            version = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
            mayor = int(version.lstrip("v").split(".")[0])
            if mayor >= 18:
                mostrar(OK, f"Node.js {version}")
            else:
                fallo(f"Node.js {version} es antiguo (se necesita 18 o superior)", "Instala Node.js LTS desde nodejs.org")
        except Exception:  # noqa: BLE001
            mostrar(AVISO, "No pude leer la versión de Node.js")
    else:
        mostrar(AVISO, "Node.js no está instalado: lo necesitas solo para las pruebas de Express (nodejs.org, versión LTS)")
    mostrar(OK if shutil.which("npm") else AVISO, "npm disponible" if shutil.which("npm") else "npm no encontrado")

    print("=" * 60)
    if criticos:
        print(f" Resultado: {criticos} problema(s) por resolver antes de continuar.")
        sys.exit(1)
    print(" Resultado: todo listo. Puedes continuar con el siguiente paso.")


if __name__ == "__main__":
    main()
