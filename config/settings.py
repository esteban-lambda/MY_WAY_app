
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p4__)#ak2&^e2o(hseuh#lu_3do)&avelva)x0#ikg%6+dp1!%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party apps
    'crispy_bootstrap5',
    'rest_framework',
    'import_export',
    'crispy_forms',
    'django_htmx',
    'simple_history',
    # my apps
    'interactions',
    'accounts',
    'contacts',
    'deals',
    'core',
    'tasks',
    'email_templates',
    'documents',
    'notifications',
    'timeline',
    'reports',
]

# Config Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myway_db',  
        'USER': 'postgres',
        'PASSWORD': 'admin123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de colores personalizados para Django Unfold
UNFOLD = {
    "SITE_TITLE": "My Way CRM",
    "SITE_HEADER": "My Way - Sistema CRM",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "Light",  # Modo claro
        "dark": lambda request: "Dark",   # Modo oscuro
    },
    "COLORS": {
        "primary": {
            "50": "rgb(248, 250, 252)",
            "100": "rgb(241, 245, 249)",
            "200": "rgb(226, 232, 240)",
            "300": "rgb(203, 213, 225)",
            "400": "rgb(148, 163, 184)",
            "500": "rgb(100, 116, 139)",
            "600": "rgb(71, 85, 105)",
            "700": "rgb(51, 65, 85)",
            "800": "rgb(30, 41, 59)",       # #1e293b - Color principal (slate-800)
            "900": "rgb(15, 23, 42)",
            "950": "rgb(2, 6, 23)",
        },
        "secondary": {
            "50": "rgb(248, 250, 252)",
            "100": "rgb(241, 245, 249)",
            "200": "rgb(226, 232, 240)",
            "300": "rgb(203, 213, 225)",
            "400": "rgb(148, 163, 184)",
            "500": "rgb(100, 116, 139)",    # #64748b - Color secundario (slate-500)
            "600": "rgb(71, 85, 105)",
            "700": "rgb(51, 65, 85)",
            "800": "rgb(30, 41, 59)",
            "900": "rgb(15, 23, 42)",
            "950": "rgb(2, 6, 23)",
        },
        "accent": {
            "50": "rgb(240, 249, 255)",
            "100": "rgb(224, 242, 254)",
            "200": "rgb(186, 230, 253)",
            "300": "rgb(125, 211, 252)",
            "400": "rgb(56, 189, 248)",
            "500": "rgb(14, 165, 233)",     # #0ea5e9 - Color de acento (sky-500)
            "600": "rgb(2, 132, 199)",
            "700": "rgb(3, 105, 161)",
            "800": "rgb(7, 89, 133)",
            "900": "rgb(12, 74, 110)",
            "950": "rgb(8, 47, 73)",
        },
    },
    "STYLES": [
        lambda request: "css/custom_admin.css",  # Archivo CSS personalizado
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": True,
                "items": [
                    {
                        "title": "Panel Principal",
                        "icon": "dashboard",
                        "link": "/",
                    },
                ],
            },
            {
                "title": "CRM",
                "separator": True,
                "items": [
                    {
                        "title": "Empresas",
                        "icon": "business",
                        "link": lambda request: "/admin/accounts/account/",
                    },
                    {
                        "title": "Contactos",
                        "icon": "contacts",
                        "link": lambda request: "/admin/contacts/contact/",
                    },
                    {
                        "title": "Tratos",
                        "icon": "handshake",
                        "link": lambda request: "/admin/deals/deal/",
                    },
                    {
                        "title": "Productos",
                        "icon": "inventory",
                        "link": lambda request: "/admin/deals/product/",
                    },
                ],
            },
            {
                "title": "Actividades",
                "separator": True,
                "items": [
                    {
                        "title": "Interacciones",
                        "icon": "forum",
                        "link": lambda request: "/admin/interactions/interaction/",
                    },
                    {
                        "title": "Llamadas",
                        "icon": "phone",
                        "link": lambda request: "/admin/interactions/call/",
                    },
                    {
                        "title": "Reuniones",
                        "icon": "event",
                        "link": lambda request: "/admin/interactions/meeting/",
                    },
                    {
                        "title": "Tareas",
                        "icon": "task_alt",
                        "link": lambda request: "/admin/tasks/task/",
                    },
                ],
            },
            {
                "title": "Herramientas",
                "separator": True,
                "items": [
                    {
                        "title": "Timeline",
                        "icon": "timeline",
                        "link": lambda request: "/admin/timeline/timelineevent/",
                    },
                    {
                        "title": "Documentos",
                        "icon": "folder",
                        "link": lambda request: "/admin/documents/document/",
                    },
                    {
                        "title": "Plantillas de Email",
                        "icon": "email",
                        "link": lambda request: "/admin/email_templates/emailtemplate/",
                    },
                    {
                        "title": "Logs de Emails",
                        "icon": "mail_outline",
                        "link": lambda request: "/admin/email_templates/emaillog/",
                    },
                    {
                        "title": "Notificaciones",
                        "icon": "notifications",
                        "link": lambda request: "/admin/notifications/notification/",
                    },
                ],
            },
            {
                "title": "Reportes",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard de Reportes",
                        "icon": "dashboard",
                        "link": lambda request: "/reports/",
                    },
                    {
                        "title": "Reporte de Ventas",
                        "icon": "trending_up",
                        "link": lambda request: "/reports/sales/",
                    },
                    {
                        "title": "Pipeline",
                        "icon": "account_tree",
                        "link": lambda request: "/reports/pipeline/",
                    },
                    {
                        "title": "Actividad",
                        "icon": "insights",
                        "link": lambda request: "/reports/activity/",
                    },
                    {
                        "title": "Cuentas",
                        "icon": "business_center",
                        "link": lambda request: "/reports/accounts/",
                    },
                ],
            },
            {
                "title": "Administración",
                "separator": True,
                "items": [
                    {
                        "title": "Usuarios",
                        "icon": "people",
                        "link": lambda request: "/admin/auth/user/",
                    },
                ],
            },
        ],
    },
}

# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email Configuration (Desarrollo - Console Backend)
# En producción, configurar con SMTP real
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@myway-crm.com'
EMAIL_HOST_USER = 'noreply@myway-crm.com'

# Para producción con SMTP (descomenta y configura):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # o tu servidor SMTP
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'tu-password-o-app-password'

# Password Reset Token Lifetime (1 día)
PASSWORD_RESET_TIMEOUT = 86400

# Session Configuration
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # True en producción con HTTPS

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# En producción con HTTPS, descomentar:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

