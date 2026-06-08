from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Client(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    
    def __str__(self):
        return self.nom

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fournisseurs')
    
    def __str__(self):
        return self.nom

class Recette(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('annule', 'Annulé'),
    ]
    
    date = models.DateField()
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='recettes')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recettes')
    
    def __str__(self):
        return f"{self.date} - {self.montant} FCFA - {self.statut}"
    
    class Meta:
        ordering = ['-date']

class Depense(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('annule', 'Annulé'),
    ]
    
    date = models.DateField()
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='depenses')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='depenses')
    
    def __str__(self):
        return f"{self.date} - {self.montant} FCFA - {self.statut}"
    
    class Meta:
        ordering = ['-date']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='Côte d\'Ivoire')
    position = models.CharField(max_length=100, blank=True, default='Comptable')
    bank_name = models.CharField(max_length=100, blank=True, default='')
    bank_account = models.CharField(max_length=50, blank=True, default='')
    bank_code = models.CharField(max_length=20, blank=True, default='')
    website = models.CharField(max_length=200, blank=True, default='')
    # Double authentification - code personnel
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_code = models.CharField(max_length=10, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

class Backup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backups')
    filename = models.CharField(max_length=255)
    size = models.IntegerField(default=0)
    record_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()
    
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('SOFT_DELETE', 'Annulation'),
    ]
    
    ENTITY_TYPES = [
        ('RECETTE', 'Recette'),
        ('DEPENSE', 'Dépense'),
        ('CLIENT', 'Client'),
        ('FOURNISSEUR', 'Fournisseur'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.IntegerField()
    entity_name = models.CharField(max_length=200, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.entity_type} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']