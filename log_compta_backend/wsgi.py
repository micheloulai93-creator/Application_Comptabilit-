import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_compta_backend.settings')

application = get_wsgi_application()

# Démarrer le scheduler de sauvegarde automatique
try:
    from backup_scheduler import scheduler
    scheduler.start()
except Exception as e:
    print(f"Erreur démarrage scheduler: {e}")