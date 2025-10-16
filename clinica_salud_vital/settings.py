"""
MÓDULO: settings.py
SISTEMA: Clinica Salud Vital
AUTOR: [Tu nombre]
SECCIÓN: [Tu sección]
AÑO: 2025

DESCRIPCIÓN GENERAL:
Configuración principal del proyecto Django para el sistema de gestión médica.
Define configuraciones de base de datos, aplicaciones, middleware y API REST.
"""

import os  # ¡AGREGA ESTA LÍNEA!
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN DE PATHS DEL PROYECTO
# =============================================================================
"""
BLOQUE: Configuración de rutas base del proyecto
OBJETIVO: Definir la estructura de directorios del sistema
"""

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# =============================================================================
"""
BLOQUE: Configuraciones de seguridad y despliegue
OBJETIVO: Garantizar la seguridad del sistema en producción
"""

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-coc5*!l-uql5hhh8#xw@z6=)#7j5_it3ya)kx3blnyr^#bva-s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# =============================================================================
# CONFIGURACIÓN DE APLICACIONES INSTALADAS
# =============================================================================
"""
BLOQUE: Registro de todas las aplicaciones Django
OBJETIVO: Habilitar funcionalidades del sistema mediante apps
"""

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'django_filters',
    'drf_yasg', 
    
    # Local apps
    'core',
]


# =============================================================================
# CONFIGURACIÓN DE MIDDLEWARE
# =============================================================================
"""
BLOQUE: Configuración de middleware para procesamiento de requests
OBJETIVO: Interceptar y procesar requests/responses HTTP
"""

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'clinica_salud_vital.urls'


# =============================================================================
# CONFIGURACIÓN DE TEMPLATES
# =============================================================================
"""
BLOQUE: Configuración del sistema de plantillas
OBJETIVO: Definir cómo se renderizan las vistas HTML
"""

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'clinica_salud_vital.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'clinica_salud_vital_db',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# =============================================================================
# CONFIGURACIÓN DE VALIDACIÓN DE CONTRASEÑAS
# =============================================================================
"""
BLOQUE: Configuración de políticas de seguridad para contraseñas
OBJETIVO: Garantizar contraseñas seguras en el sistema
"""

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# CONFIGURACIÓN INTERNACIONALIZACIÓN
# =============================================================================
"""
BLOQUE: Configuración de idioma y zona horaria
OBJETIVO: Adaptar el sistema al locale específico
"""

LANGUAGE_CODE = 'es-cl'  # Cambiado a español de Chile

TIME_ZONE = 'America/Santiago'  # Cambiado a zona horaria de Chile

USE_I18N = True

USE_TZ = True


# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# =============================================================================
"""
BLOQUE: Configuración para archivos CSS, JavaScript e imágenes
OBJETIVO: Servir archivos estáticos correctamente
"""

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core/static'),  # ¡CORREGIDO!
]


# =============================================================================
# CONFIGURACIÓN DE CLAVE PRIMARIA POR DEFECTO
# =============================================================================
"""
BLOQUE: Configuración del tipo de campo para claves primarias
OBJETIVO: Definir el comportamiento de IDs automáticos
"""

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# CONFIGURACIÓN DJANGO REST FRAMEWORK
# =============================================================================
"""
BLOQUE: Configuración completa de la API REST
OBJETIVO: Habilitar funcionalidades avanzadas de API para el sistema médico
"""

REST_FRAMEWORK = {
    # Renderers: Define cómo se formatea la respuesta
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # Solo respuestas JSON
    ],
    
    # Parsers: Define cómo se procesan los datos entrantes
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',  # Solo acepta JSON
    ],
    
    # Filtros: Habilita sistema de filtrado avanzado
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # Filtros personalizados
        'rest_framework.filters.SearchFilter',  # Búsqueda textual
    ],
    
    # Paginación: Controla cómo se dividen los resultados grandes
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10  # 10 elementos por página
}