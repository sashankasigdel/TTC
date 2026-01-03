from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notes.urls')),
]

if settings.DEBUG:
    # Serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve media files ← ADD THIS LINE!
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)