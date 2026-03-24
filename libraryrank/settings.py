"""
LibraryRank — Settings
Main DB  : MySQL / MariaDB  (LibraryRank app tables)
Koha DB  : MySQL / MariaDB  (Koha ILS — read-only, same server different database)
SSO      : CAS (university single sign-on)
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY   = env('SECRET_KEY', default='django-insecure-change-me')
DEBUG        = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '*'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cas_ng',
    'leaderboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'libraryrank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'leaderboard.context_processors.cas_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'libraryrank.wsgi.application'

# ─────────────────────────────────────────────────────────────
# DATABASES
#
# 'default'  →  LibraryRank's OWN tables (Django writes here)
#               MySQL/MariaDB, separate database from Koha
#
# 'koha'     →  Koha ILS database (READ-ONLY)
#               Usually on the same MySQL/MariaDB server, just a
#               different database name (e.g. "koha" or "koha_library")
#               Django never migrates or writes to this database.
# ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     env('DB_NAME',     default='libraryrank_db'),
        'USER':     env('DB_USER',     default='libraryrank_user'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST':     env('DB_HOST',     default='127.0.0.1'),
        'PORT':     env('DB_PORT',     default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    'koha': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     env('KOHA_DB_NAME',     default='koha'),
        'USER':     env('KOHA_DB_USER',     default='koha'),
        'PASSWORD': env('KOHA_DB_PASSWORD', default=''),
        'HOST':     env('KOHA_DB_HOST',     default='127.0.0.1'),
        'PORT':     env('KOHA_DB_PORT',     default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {'NAME': None},  # never create test DB from Koha connection
    },
}

# Route all Django ORM operations to 'default'.
# 'koha' is only accessed via raw SQL in the sync command.
DATABASE_ROUTERS = ['libraryrank.db_routers.KohaReadOnlyRouter']

# ─────────────────────────────────────────────────────────────
# CAS SSO
# ─────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
]

CAS_SERVER_URL           = env('CAS_SERVER_URL', default='https://sso.university.ac.id/cas/')
CAS_VERSION              = env('CAS_VERSION',    default='3')
CAS_CREATE_USER          = True
CAS_APPLY_ATTRIBUTES_TO_USER = True
CAS_RENAME_ATTRIBUTES    = {
    'cn':   'first_name',
    'sn':   'last_name',
    'mail': 'email',
}
CAS_LOCAL_DEV = env.bool('CAS_LOCAL_DEV', default=False)

LOGIN_URL           = 'cas_ng_login'
LOGOUT_URL          = 'cas_ng_logout'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'

# ─────────────────────────────────────────────────────────────
# KOHA SYNC — patron category → role mapping
# Adjust to match your university's Koha categorycode values.
# Run: python manage.py sync_from_koha
# ─────────────────────────────────────────────────────────────
KOHA_STUDENT_CATEGORIES  = env.list('KOHA_STUDENT_CATEGORIES',  default=['S', 'ST', 'STUDENT', 'MAHASISWA'])
KOHA_LECTURER_CATEGORIES = env.list('KOHA_LECTURER_CATEGORIES', default=['L', 'LEC', 'DOSEN', 'FACULTY'])
KOHA_STAFF_CATEGORIES    = env.list('KOHA_STAFF_CATEGORIES',    default=['STAFF', 'STF', 'KARYAWAN', 'PEGAWAI'])

# Koha branchcode → faculty display name
KOHA_BRANCH_FACULTY_MAP = {
    'CS':  'Computer Science',
    'ENG': 'Engineering',
    'MED': 'Medicine',
    'ECO': 'Economics',
    'LAW': 'Law',
    'PSY': 'Psychology',
    'ARC': 'Architecture',
    'BIO': 'Biology',
}

# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Jakarta'
USE_I18N      = True
USE_TZ        = True

STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
