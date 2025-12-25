# notes/apps.py
from django.apps import AppConfig

class NotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notes'
    
    def ready(self):
        # Import signals
        import notes.signals
        print("✓ Signals loaded for notes app")