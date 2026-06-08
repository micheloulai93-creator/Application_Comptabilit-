from .models import AuditLog

def log_action(user, action, entity_type, entity_id, entity_name='', details=None):
    """
    Enregistre une action dans l'historique (AuditLog)
    """
    print(f"🔍 [DEBUG] log_action appelée - user: {user}, action: {action}, entity_type: {entity_type}")
    
    if user and user.is_authenticated:
        try:
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name[:200] if entity_name else '',
                details=details or {}
            )
            print(f"✅ [DEBUG] Log créé avec succès - ID: {audit_log.id}")
            return audit_log
        except Exception as e:
            print(f"❌ [DEBUG] Erreur création log: {e}")
            return None
    else:
        print(f"❌ [DEBUG] Utilisateur non authentifié ou inexistant: {user}")
        return None


def test_log():
    """Fonction de test pour vérifier que le logging fonctionne"""
    from django.contrib.auth.models import User
    user = User.objects.first()
    if user:
        return log_action(user, 'CREATE', 'RECETTE', 999, 'Test manuel', {'test': 'ok'})
    return None