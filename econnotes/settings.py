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
EMAIL_HOST_PASSWORD = 'pscqgxoxrdjmjgez'  # Your actual Gmail password

# Sender info
DEFAULT_FROM_EMAIL = 'The Tuition Class <sashankadada36@gmail.com>'
SERVER_EMAIL = 'sashankadada36@gmail.com'
# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-12345-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

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
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'econnotes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Your HTML files
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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'frontend/media')

# settings.py - Add to the bottom


# Jazzmin Settings
JAZZMIN_SETTINGS = {
    "custom_css": "admin/css/custom.css",
    # ── Branding ──────────────────────────────────────────────────────────────
    "site_title": "Notes Admin",
    "site_header": "Notes",
    "site_brand": "Notes",
    "site_logo": None,                   # e.g. "admin/img/logo.png"
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": "Welcome back 👋",
    "copyright": "Notes App",
 
    # ── Top navigation links ───────────────────────────────────────────────────
    "topmenu_links": [
        {"name": "Dashboard",      "url": "admin:index",        "permissions": ["auth.view_user"]},
        {"name": "System Report",  "url": "/admin/notes/premiumsubscription/system-report/"},
        {"name": "View Site",      "url": "/",                  "new_window": True},
    ],
 
    # ── User menu (top-right avatar dropdown) ─────────────────────────────────
    "usermenu_links": [
        {"name": "View Site", "url": "/", "new_window": True, "icon": "ti ti-external-link"},
    ],
 
    # ── Sidebar icons (app_label.ModelName) ───────────────────────────────────
    "icons": {
        "auth":                        "ti ti-shield",
        "auth.user":                   "ti ti-users",
        "auth.group":                  "ti ti-shield-half",
        "notes.userprofile":           "ti ti-user-check",
        "notes.course":                "ti ti-book",
        "notes.subject":               "ti ti-notes",
        "notes.chapter":               "ti ti-file-text",
        "notes.payment":               "ti ti-credit-card",
        "notes.premiumsubscription":   "ti ti-crown",
    },
    "default_icon_parents":  "ti ti-folder",
    "default_icon_children": "ti ti-circle",
 
    # ── Sidebar ordering ──────────────────────────────────────────────────────
    "order_with_respect_to": [
        "notes",
        "notes.payment",
        "notes.premiumsubscription",
        "notes.userprofile",
        "notes.course",
        "notes.subject",
        "notes.chapter",
        "auth",
    ],
 
    # ── Hide anything you don't need ──────────────────────────────────────────
    "hide_apps":   [],
    "hide_models": [],
 
    # ── UI behaviour ──────────────────────────────────────────────────────────
    "show_sidebar":           True,
    "navigation_expanded":    True,
    "changeform_format":      "horizontal_tabs",   # cleaner edit pages
    "related_modal_active":   True,                # open related objects in a modal
    "show_ui_builder":        False,               # hide the UI builder in production
 
    # ── Search ────────────────────────────────────────────────────────────────
    "search_model": ["auth.user", "notes.payment", "notes.premiumsubscription"],
}
 
JAZZMIN_UI_TWEAKS = {
    # ── Navbar ────────────────────────────────────────────────────────────────
    "navbar_small_text":  False,
    "navbar":             "navbar-dark",
    "no_navbar_border":   True,
    "navbar_fixed":       True,           # sticks to top while scrolling
 
    # ── Sidebar ───────────────────────────────────────────────────────────────
    "sidebar":                    "sidebar-dark-primary",
    "sidebar_fixed":              True,
    "sidebar_nav_small_text":     False,
    "sidebar_nav_child_indent":   True,
    "sidebar_nav_compact_style":  True,
    "sidebar_nav_flat_style":     False,
    "sidebar_disable_expand":     False,
 
    # ── Brand ─────────────────────────────────────────────────────────────────
    "brand_colour":       "navbar-dark",
    "brand_small_text":   False,
 
    # ── Body ──────────────────────────────────────────────────────────────────
    "body_small_text":    False,
    "footer_small_text":  False,
    "footer_fixed":       False,
    "layout_boxed":       False,
 
    # ── Accent & theme ────────────────────────────────────────────────────────
    "accent": "accent-primary",
    "theme":  "default",          # base AdminLTE theme; our CSS overrides on top
 
    # ── Button classes ────────────────────────────────────────────────────────
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-outline-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
 
    # ── Actions bar ───────────────────────────────────────────────────────────
    "actions_sticky_top": True,
}


