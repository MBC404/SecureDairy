from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY & DEBUG ---
# The SECRET_KEY is read from the Render environment variable. 
# If it's not found (e.g., local test), it uses a default insecure key.
# In production, the environment variable MUST be set.
SECRET_KEY = os.environ.get('SECRET_KEY')

# DEBUG is read from the Render environment variable (set to 'False' in production).
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS is read from the Render environment variable (e.g., 'securedairy.onrender.com').
# The .split(',') handles multiple hosts if needed.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')



# --- APPS ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'letters',
]


# --- MIDDLEWARE ---

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be listed directly after SecurityMiddleware for static files
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Added missing default middleware
]


# --- URLS / WSGI ---

ROOT_URLCONF = 'letterbox.urls'

WSGI_APPLICATION = 'letterbox.wsgi.application'


# --- TEMPLATES ---

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
        },
    },
]


# --- DATABASE (The Fix for 500 Error) ---

# This configuration reads the full PostgreSQL connection string from 
# the 'DATABASE_URL' environment variable set on Render.
DATABASES = {
    'default': dj_database_url.config(
        # CRITICAL: This line tells dj-database-url where to find the connection string.
        default=os.environ.get('DATABASE_URL'), 
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# --- STATIC FILES (WhiteNoise) ---

# The URL path for static files (e.g., /static/styles.css)
STATIC_URL = '/static/'

# The directory where 'collectstatic' will place all the static files 
# for WhiteNoise to serve.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuration for WhiteNoise to handle static files efficiently
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- AUTHENTICATION ---
# (Add these if they were not already present)

# Password validation
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True