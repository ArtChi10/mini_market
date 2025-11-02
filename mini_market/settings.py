"""
Django settings for mini_market project.

База: Django 5.2.x
Особенности:
- Чтение конфигурации из .env (django-environ)
- RU/Asia/Tbilisi
- Статика/медиа настроены
- БД по умолчанию sqlite, но можно переопределить DATABASE_URL в .env
"""

from pathlib import Path
import environ
import os

# -------------------------------------------------------------------
# БАЗОВЫЕ ПУТИ
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../mini_market (где manage.py — на уровень выше)

# -------------------------------------------------------------------
# ENV-ПЕРЕМЕННЫЕ
# -------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "unsafe-secret-key"),
    ALLOWED_HOSTS=(list, []),          # пример в .env: ALLOWED_HOSTS=127.0.0.1,localhost
    CSRF_TRUSTED_ORIGINS=(list, []),   # пример в .env: CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000
    LANGUAGE_CODE=(str, "ru"),
    TIME_ZONE=(str, "Asia/Tbilisi"),
    PROJECT_TITLE=(str, "мини-маркет"),
)
# .env лежит рядом с manage.py (в корне проекта)
environ.Env.read_env(str(BASE_DIR / ".env"))
LOGIN_REDIRECT_URL = "portfolio"   # после входа — на портфель
LOGOUT_REDIRECT_URL = "login"      # после выхода — на форму логина

PRICE_CHANGE_MIN = env.int("PRICE_CHANGE_MIN", default=5)
PRICE_CHANGE_MAX = env.int("PRICE_CHANGE_MAX", default=20)
DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Проектная «лейбла» — можно показывать в шаблонах
PROJECT_TITLE = env("PROJECT_TITLE")

# -------------------------------------------------------------------
# ПРИЛОЖЕНИЯ
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "catalog",
    "trade",
    # сюда позже добавим: users, catalog, trade и т.д.
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mini_market.urls"

# -------------------------------------------------------------------
# ШАБЛОНЫ
# -------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # собственная папка с шаблонами проекта
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mini_market.wsgi.application"
ASGI_APPLICATION = "mini_market.asgi.application"

# -------------------------------------------------------------------
# БАЗА ДАННЫХ
# -------------------------------------------------------------------
# По умолчанию sqlite, но можно переопределить через .env:
# DATABASE_URL=postgres://user:pass@host:port/dbname
DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# -------------------------------------------------------------------
# ПАРОЛИ
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# ЛОКАЛИЗАЦИЯ/ВРЕМЯ
# -------------------------------------------------------------------
LANGUAGE_CODE = env("LANGUAGE_CODE")
TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# СТАТИКА И МЕДИА
# -------------------------------------------------------------------
# В dev Django сам раздаёт STATIC_URL
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # для collectstatic при деплое

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------------------------------------
# ПРОЧЕЕ
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# При желании: логотип/бренд в шаблонах из settings
# В шаблонах доступно: {{ settings.PROJECT_TITLE }}
# mini_market/settings.py
ALLOWED_HOSTS = [
    "127.0.0.1", "localhost",
    ".ngrok-free.dev",      # <-- добавили dev
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://*.ngrok-free.app",
]

# чтобы Django корректно определял, что запрос пришёл по https через прокси
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


