import threading
import time
from datetime import datetime
import json
import os
import django

# Configurer Django avant les imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_compta_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Recette, Depense, Client, Fournisseur, Backup

class BackupScheduler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.is_running = False
            cls._instance.interval_seconds = 86400  # 24 heures
        return cls._instance
    
    def start(self):
        if self.is_running:
            return
        self.is_running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print(f"[{datetime.now()}] Sauvegarde automatique démarrée (intervalle: {self.interval_seconds//3600}h)")
    
    def stop(self):
        self.is_running = False
    
    def _run(self):
        while self.is_running:
            time.sleep(self.interval_seconds)
            self.perform_backup()
    
    def perform_backup(self):
        try:
            print(f"[{datetime.now()}] Exécution sauvegarde automatique...")
            
            recettes = list(Recette.objects.values())
            depenses = list(Depense.objects.values())
            clients = list(Client.objects.values())
            fournisseurs = list(Fournisseur.objects.values())
            
            data = {
                'recettes': recettes,
                'depenses': depenses,
                'clients': clients,
                'fournisseurs': fournisseurs,
                'export_date': datetime.now().isoformat(),
                'version': '2.0',
                'type': 'automatique'
            }
            
            json_data = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                Backup.objects.create(
                    user=admin_user,
                    filename=f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    size=len(json_data),
                    record_count=len(recettes) + len(depenses) + len(clients) + len(fournisseurs)
                )
            
            # Créer le dossier backups s'il n'existe pas
            os.makedirs('backups', exist_ok=True)
            
            with open(f"backups/auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            print(f"[{datetime.now()}] Sauvegarde automatique terminée ({len(json_data)} octets)")
            
        except Exception as e:
            print(f"[{datetime.now()}] Erreur sauvegarde auto: {e}")

# Démarrer le scheduler
scheduler = BackupScheduler()