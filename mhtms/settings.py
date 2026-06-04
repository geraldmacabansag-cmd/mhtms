from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core ──────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-local-dev-key-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'crispy_forms',
    'crispy_bootstrap5',
    # ── DevSecOps apps (Member 5) ──────────────────────────────────────
    'axes',        # login lockout / brute-force protection
    'honeypot',    # honeypot trap field on login form
    # ── Project apps ──────────────────────────────────────────────────
    'accounts',
    'patients',
    'triage',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ── django-axes middleware — must be LAST in the list ──────────────
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'mhtms.urls'

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
            ],
            'libraries': {
                'triage_tags': 'triage.templatetags.triage_tags',
            },
        },
    },
]

WSGI_APPLICATION = 'mhtms.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────
DATABASE_URL = config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# ── Auth ──────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# django-axes requires this backend in addition to the default one
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # axes lockout check — must be FIRST
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Localisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# ── Static files ──────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Crispy ────────────────────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ── DRF + Rate Limiting (Member 5) ───────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT — primary
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Rate limiting — prevents API scraping and brute-force enumeration
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',   # unauthenticated users
        'rest_framework.throttling.UserRateThrottle',   # authenticated users
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/hour',   # max 30 requests per hour for public
        'user': '300/hour',  # max 300 requests per hour for logged-in users
    },
}

# ── Simple JWT Configuration (Member 2) ──────────────────────────────
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=60),   # access token expires in 60 min
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),        # refresh token valid for 1 day
    'ROTATE_REFRESH_TOKENS':  True,                     # new refresh token issued on each refresh
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),                  # Authorization: Bearer <token>
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ── django-axes — Login Lockout (Member 5) ────────────────────────────
# Locks out a user after 5 failed login attempts within 1 hour
AXES_FAILURE_LIMIT       = 5          # number of failed attempts before lockout
AXES_COOLOFF_TIME        = 1          # lockout duration in hours
AXES_LOCKOUT_CALLABLE    = None       # use default lockout response
AXES_RESET_ON_SUCCESS    = True       # reset fail count after successful login
AXES_ENABLE_ADMIN        = True       # show lockout records in Django admin
AXES_VERBOSE             = True       # log lockout events to console
AXES_LOCKOUT_PARAMETERS  = ['username']  # lock by username only — other accounts on same IP stay accessible

# ── django-honeypot — Bot Trap on Login Form (Member 5) ───────────────
# Adds a hidden field to the login form. Real users never fill it.
# If a bot fills it in, the submission is silently blocked.
HONEYPOT_FIELD_NAME      = 'phone_number'   # hidden field name
HONEYPOT_VALUE           = ''               # must be empty — bots fill it in
HONEYPOT_RESPONDER       = 'honeypot.views.honeypot_error'  # what to show if triggered

# ── Security Headers ──────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS            = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

if not DEBUG:
    SECURE_SSL_REDIRECT          = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE        = True
    CSRF_COOKIE_SECURE           = True
    SECURE_HSTS_SECONDS          = 31536000   # 1 year HSTS header
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD          = True

# Custom lockout page shown when axes blocks a user
AXES_LOCKOUT_TEMPLATE = '403_axes.html'
