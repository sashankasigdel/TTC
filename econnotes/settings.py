"""
Django settings for econnotes project.
"""

from pathlib import Path
import os
# settings.py - REAL EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# USE YOUR REAL GMAIL CREDENTIALS
EMAIL_HOST_USER = 'sashankadada36@gmail.com'  # Your actual Gmail
EMAIL_HOST_PASSWORD = 'ijza lwtz xzoc zukg'  # Your actual Gmail password

# Sender info
DEFAULT_FROM_EMAIL = 'The Tuition Class <thetuitionclass01@gmail.com>'
SERVER_EMAIL = 'thetuitionclass01@gmail.com'
# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-12345-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your apps
    'notes',
    'users',
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

ROOT_URLCONF = 'econnotes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'frontend/templates',  # Your HTML files
        ],
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

WSGI_APPLICATION = 'econnotes.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/static',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# For production, you'll need this later
STATIC_ROOT = BASE_DIR / 'staticfiles'

# settings.py - Add to the bottom


# Jazzmin Settings
JAZZMIN_SETTINGS = {
    # Title on the brand (19 chars max)
    "site_brand": "The Tuition Class Admin",
    
    # Logo to use for your site, must be present in static files
    "site_logo": "books.ico",
    
    # Welcome text on the login screen
    "welcome_sign": "Welcome to The Tuition Class Admin Panel",
    
    # Copyright on the footer
    "copyright": "The Tuition Class",
    
    # The model admin to search from the search bar
    "search_model": "auth.User",
    
    # Field name on user model that contains avatar image
    "user_avatar": None,
    
    # Top Menu Links
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Website", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"app": "notes"},
    ],
    
    # Custom icons for side menu apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "notes": "fas fa-sticky-note",
    },
    
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # UI Tweaks
    "show_ui_builder": True,  # Allows customizing the UI
    
    # Change default theme
    "theme": "darkly",  # You can try: "darkly", "flatly", "slate", "solar", "superhero"
    
    # Custom links on the side menu
    "custom_links": {
        "notes": [{
            "name": "View Website", 
            "url": "/", 
            "icon": "fas fa-external-link-alt",
            "permissions": ["auth.view_user"]
        }]
    },
}


