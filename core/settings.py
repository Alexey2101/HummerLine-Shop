import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS handling
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    'hummerline.up.railway.app',
]

# Add specific Railway domains if they exist in env
for env_var in ['RAILWAY_PUBLIC_DOMAIN', 'RAILWAY_STATIC_URL']:
    domain = os.environ.get(env_var)
    if domain:
        ALLOWED_HOSTS.append(domain)

# CSRF_TRUSTED_ORIGINS handling
CSRF_TRUSTED_ORIGINS = [
    'https://hummerline.up.railway.app',
    'https://hummerline-shop-production.up.railway.app',
]

# Dynamic CSRF origins from Railway
for env_var in ['RAILWAY_PUBLIC_DOMAIN', 'RAILWAY_STATIC_URL']:
    domain = os.environ.get(env_var)
    if domain:
        if not domain.startswith('http'):
            CSRF_TRUSTED_ORIGINS.append(f"https://{domain}")
        else:
            CSRF_TRUSTED_ORIGINS.append(domain)

# Additional custom origins from env
custom_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS')
if custom_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in custom_csrf.split(',') if o.strip()])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'shop.apps.ShopConfig', # Наше приложение HummerLine
]

# Поддержка удалённого хранения медиа (S3 / S3-совместимые хранилища, напр. Railway Buckets)
# Будет включена, если в окружении указать USE_S3=true

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security Settings
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

ROOT_URLCONF = 'core.urls'

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
                'core.context_processors.simple_design',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Use dj-database-url to parse the DATABASE_URL
    # For Railway internal connections, SSL is often not required and can cause issues if forced
    is_private = 'RAILWAY_PRIVATE_DOMAIN' in database_url or '.internal' in database_url
    
    DATABASES['default'] = dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=False if is_private else not DEBUG,
    )
elif not DEBUG:
    # Fallback for individual environment variables if DATABASE_URL is missing
    pg_user = os.environ.get('PGUSER')
    pg_pass = os.environ.get('PGPASSWORD')
    pg_host = os.environ.get('PGHOST')
    pg_port = os.environ.get('PGPORT')
    pg_db = os.environ.get('PGDATABASE')
    
    if all([pg_user, pg_pass, pg_host, pg_port, pg_db]):
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': pg_db,
            'USER': pg_user,
            'PASSWORD': pg_pass,
            'HOST': pg_host,
            'PORT': pg_port,
        }
    else:
        # Защита от случайного использования SQLite в продакшене
        raise Exception("DATABASE_URL or PGDATABASE/PGHOST/... must be set in production (DEBUG=False)")


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Простой режим хранения пользовательских файлов в S3-совместимом бакете (Railway Buckets или AWS S3).
# Включается установкой переменной окружения `USE_S3=true`.
USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'
if USE_S3:
    INSTALLED_APPS.append('storages')

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', None)
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')  # optional for S3-compatible providers

    # Используем стандартный бекенд django-storages (минимальная настройка)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    # Простая логика MEDIA_URL: если задан endpoint, используем path-style URL, иначе стандартный S3 host
    if AWS_S3_ENDPOINT_URL:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
    else:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"

# CORS (для доступа к медиа с клиентских доменов, если требуется)
# Укажите CORS_ALLOWED_ORIGINS как через переменную окружения (comma-separated),
# или разрешите все с CORS_ALLOW_ALL_ORIGINS=true (не рекомендовано в продакшене).
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
if not CORS_ALLOW_ALL_ORIGINS:
    cors_env = os.environ.get('CORS_ALLOWED_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_env.split(',') if o.strip()]
else:
    CORS_ALLOWED_ORIGINS = []

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Flag to enable simplified/legacy design (set SIMPLE_DESIGN=true in env to enable)
SIMPLE_DESIGN = os.environ.get('SIMPLE_DESIGN', 'False').lower() == 'true'
