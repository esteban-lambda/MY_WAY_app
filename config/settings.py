
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
            "50": "rgb(235, 240, 249)",
            "100": "rgb(215, 225, 243)",
            "200": "rgb(175, 195, 231)",
            "300": "rgb(135, 165, 219)",
            "400": "rgb(95, 135, 207)",
            "500": "rgb(26, 50, 99)",       # #1A3263 - Color principal
            "600": "rgb(21, 40, 79)",
            "700": "rgb(16, 30, 59)",
            "800": "rgb(11, 20, 40)",
            "900": "rgb(6, 10, 20)",
            "950": "rgb(3, 5, 10)",
        },
        "secondary": {
            "50": "rgb(240, 245, 248)",
            "100": "rgb(225, 235, 241)",
            "200": "rgb(195, 215, 229)",
            "300": "rgb(165, 195, 217)",
            "400": "rgb(135, 175, 205)",
            "500": "rgb(84, 119, 146)",     # #547792 - Color secundario
            "600": "rgb(67, 95, 117)",
            "700": "rgb(50, 71, 88)",
            "800": "rgb(34, 48, 58)",
            "900": "rgb(17, 24, 29)",
            "950": "rgb(8, 12, 15)",
        },
        "accent": {
            "50": "rgb(255, 251, 245)",
            "100": "rgb(255, 247, 235)",
            "200": "rgb(254, 238, 215)",
            "300": "rgb(253, 230, 195)",
            "400": "rgb(252, 221, 175)",
            "500": "rgb(250, 185, 91)",     # #FAB95B - Color de acento
            "600": "rgb(248, 170, 61)",
            "700": "rgb(220, 145, 40)",
            "800": "rgb(180, 115, 30)",
            "900": "rgb(140, 85, 20)",
            "950": "rgb(100, 55, 10)",
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
