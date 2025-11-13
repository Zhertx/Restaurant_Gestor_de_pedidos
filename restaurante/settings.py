"""
Django settings for restaurante project.
Generado con Django 5.2.8 y preparado para despliegue (Render) y entorno local.
"""

from pathlib import Path
import os

# --- Rutas base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Helpers para variables de entorno ---
def _list_env(name: str, default: str = "") -> list[str]:
    """Lee una variable de entorno separada por comas y devuelve lista limpia."""
    raw = os.getenv(name, default) or ""
    return [s.strip() for s in raw.split(",") if s.strip()]

def _bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}

# --- Flags / Integraciones (M1/M4) ---
USE_MOCKS = _bool_env("USE_MOCKS", True)  # déjalo True para la demo
M3_WEBHOOK_SECRET = os.getenv("M3_WEBHOOK_SECRET", "dev-secret")

# Si USE_MOCKS=True, puedes apuntar M1/M4 a los endpoints locales /mock
M1_BASE_URL = os.getenv("M1_BASE_URL", "http://127.0.0.1:8000/mock")
M4_BASE_URL = os.getenv("M4_BASE_URL", "http://127.0.0.1:8000/mock")

# --- Seguridad / Entorno ---
# ¡No hardcodear claves en producción!
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
DEBUG = _bool_env("DEBUG", True)

# En local: 127.0.0.1,localhost
# En Render: poner tu dominio exacto, ej: restaurant-gestor-de-pedidos.onrender.com
ALLOWED_HOSTS = _list_env("ALLOWED_HOSTS", "127.0.0.1,localhost")
# En Render usa https://<tu-dominio>
CSRF_TRUSTED_ORIGINS = _list_env("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1,http://localhost")

# Endurecimiento mínimo cuando no estamos en DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "pedidos",
    "mock",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # estáticos en prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "restaurante.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "restaurante.wsgi.application"

# --- DB: usar carpeta escribible en Render (/var/data) ---
# Fallback local si no existe env.
DEFAULT_SQLITE = str(BASE_DIR / "db.sqlite3")
SQLITE_PATH = os.getenv("SQLITE_PATH", "/var/data/db.sqlite3")

# Crea carpeta sólo si apunta a /var/... (en build de Render aún puede no existir; no es crítico si falla)
try:
    if SQLITE_PATH.startswith("/var/"):
        os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
except Exception:
    pass

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SQLITE_PATH or DEFAULT_SQLITE,
    }
}

# --- Validadores de contraseña ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalización ---
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Santiago"  # Chile
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos (Whitenoise + Django 5) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- DRF (opcional) ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# --- Clave primaria por defecto ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
