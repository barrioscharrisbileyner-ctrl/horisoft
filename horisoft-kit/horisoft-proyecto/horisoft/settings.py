"""
Configuración del proyecto Horisoft.

Entorno académico: Windows · Python · VS Code · Laragon (MySQL) · Django
(mismo entorno usado en la guía TallerExpress).
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------------
# Seguridad básica (uso académico / desarrollo local)
# -------------------------------------------------------------------------
SECRET_KEY = 'django-insecure-horisoft-clave-de-desarrollo-cambia-esto-en-produccion'

DEBUG = True

# '*' solo para la demo en red local durante la clase (ver guía Entrega 2,
# sección 8). En producción real se listan los dominios/IP exactos.
ALLOWED_HOSTS = ['*']

# -------------------------------------------------------------------------
# Apps instaladas
# -------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'residentes',  # nuestra app: Personas, Unidades Residenciales y Residencias
    'usuarios',    # autenticación y roles
    'reservas',    # zonas comunes y reservas
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'horisoft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # Django busca templates dentro de residentes/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuarios.context_processors.rol_actual',
            ],
        },
    },
]

WSGI_APPLICATION = 'horisoft.wsgi.application'

# -------------------------------------------------------------------------
# Base de datos: MySQL servido por Laragon
# -------------------------------------------------------------------------
# Antes de migrar, crea la base vacía 'horisoft_db' desde Laragon
# (Menú → MySQL → phpMyAdmin/HeidiSQL → Crear base de datos "horisoft_db",
# colación recomendada: utf8mb4_general_ci).
#
# Laragon por defecto usa el usuario 'root' SIN contraseña. Si tu Laragon
# tiene una contraseña distinta, cámbiala abajo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'horisoft_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# -------------------------------------------------------------------------
# Validación de contraseñas (usuarios del admin de Django)
# -------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------------
# Internacionalización — mensajes de validación en español
# -------------------------------------------------------------------------
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------------
# Archivos estáticos
# -------------------------------------------------------------------------
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Autenticación y roles (app usuarios)
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'usuarios:inicio'
LOGOUT_REDIRECT_URL = 'usuarios:login'
