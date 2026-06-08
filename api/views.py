from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime
import json
from decimal import Decimal
from .models import Recette, Depense, Client, Fournisseur, UserProfile, Backup, AuditLog
from .serializers import (
    RecetteSerializer, DepenseSerializer, 
    ClientSerializer, FournisseurSerializer,
    UserSerializer
)
from .utils import log_action

# ==================== CLIENTS ET FOURNISSEURS ====================

@method_decorator(csrf_exempt, name='dispatch')
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('nom')
    serializer_class = ClientSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        user_id = self.request.data.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        return None
    
    def perform_create(self, serializer):
        user = self.get_user()
        instance = serializer.save(user=user)
        log_action(
            user=user,
            action='CREATE',
            entity_type='CLIENT',
            entity_id=instance.id,
            entity_name=instance.nom,
            details={'telephone': instance.telephone, 'email': instance.email}
        )
    
    def perform_update(self, serializer):
        user = self.get_user()
        old_instance = self.get_object()
        instance = serializer.save()
        log_action(
            user=user,
            action='UPDATE',
            entity_type='CLIENT',
            entity_id=instance.id,
            entity_name=instance.nom,
            details={'before': {'nom': old_instance.nom}, 'after': {'nom': instance.nom}}
        )
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_user()
        instance = self.get_object()
        log_action(
            user=user,
            action='DELETE',
            entity_type='CLIENT',
            entity_id=instance.id,
            entity_name=instance.nom
        )
        return super().destroy(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all().order_by('nom')
    serializer_class = FournisseurSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        user_id = self.request.data.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        return None
    
    def perform_create(self, serializer):
        user = self.get_user()
        instance = serializer.save(user=user)
        log_action(
            user=user,
            action='CREATE',
            entity_type='FOURNISSEUR',
            entity_id=instance.id,
            entity_name=instance.nom,
            details={'telephone': instance.telephone, 'email': instance.email}
        )
    
    def perform_update(self, serializer):
        user = self.get_user()
        old_instance = self.get_object()
        instance = serializer.save()
        log_action(
            user=user,
            action='UPDATE',
            entity_type='FOURNISSEUR',
            entity_id=instance.id,
            entity_name=instance.nom,
            details={'before': {'nom': old_instance.nom}, 'after': {'nom': instance.nom}}
        )
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_user()
        instance = self.get_object()
        log_action(
            user=user,
            action='DELETE',
            entity_type='FOURNISSEUR',
            entity_id=instance.id,
            entity_name=instance.nom
        )
        return super().destroy(request, *args, **kwargs)

# ==================== RECETTES ====================

@method_decorator(csrf_exempt, name='dispatch')
class RecetteViewSet(viewsets.ModelViewSet):
    serializer_class = RecetteSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Recette.objects.filter(statut='actif').order_by('-date')
    
    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        user_id = self.request.data.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        return None
    
    def perform_create(self, serializer):
        user = self.get_user()
        instance = serializer.save(user=user)
        log_action(
            user=user,
            action='CREATE',
            entity_type='RECETTE',
            entity_id=instance.id,
            entity_name=instance.description[:100] if instance.description else f"Recette {instance.id}",
            details={'montant': str(instance.montant), 'date': str(instance.date)}
        )
    
    def perform_update(self, serializer):
        user = self.get_user()
        old_instance = self.get_object()
        instance = serializer.save()
        log_action(
            user=user,
            action='UPDATE',
            entity_type='RECETTE',
            entity_id=instance.id,
            entity_name=instance.description[:100] if instance.description else f"Recette {instance.id}",
            details={'before': {'montant': str(old_instance.montant)}, 'after': {'montant': str(instance.montant)}}
        )
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_user()
        instance = self.get_object()
        instance.statut = 'annule'
        instance.save()
        log_action(
            user=user,
            action='SOFT_DELETE',
            entity_type='RECETTE',
            entity_id=instance.id,
            entity_name=instance.description[:100] if instance.description else f"Recette {instance.id}"
        )
        return Response({'message': 'Recette annulée avec succès'}, status=status.HTTP_200_OK)

# ==================== DÉPENSES ====================

@method_decorator(csrf_exempt, name='dispatch')
class DepenseViewSet(viewsets.ModelViewSet):
    serializer_class = DepenseSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Depense.objects.filter(statut='actif').order_by('-date')
    
    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        user_id = self.request.data.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        return None
    
    def perform_create(self, serializer):
        user = self.get_user()
        instance = serializer.save(user=user)
        log_action(
            user=user,
            action='CREATE',
            entity_type='DEPENSE',
            entity_id=instance.id,
            entity_name=instance.description[:100] if instance.description else f"Dépense {instance.id}",
            details={'montant': str(instance.montant), 'date': str(instance.date)}
        )
    
    def perform_update(self, serializer):
        user = self.get_user()
        old_instance = self.get_object()
        instance = serializer.save()
        log_action(
            user=user,
            action='UPDATE',
            entity_type='DEPENSE',
            entity_id=instance.id,
            entity_name=instance.description[:100] if instance.description else f"Dépense {instance.id}",
            details={'before': {'montant': str(old_instance.montant)}, 'after': {'montant': str(instance.montant)}}
        )
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_user()
        instance = self.get_object()
        instance.statut = 'annule'
        instance.save()
        log_action(
            user=user,
            action='SOFT_DELETE',
            entity_type='DEPENSE',
            entity_id=instance.id,
            entity_name=instance.description[:100] if instance.description else f"Dépense {instance.id}"
        )
        return Response({'message': 'Dépense annulée avec succès'}, status=status.HTTP_200_OK)

# ==================== VUES D'AUTHENTIFICATION ====================

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        
        if not username:
            return Response({'error': 'Nom d\'utilisateur requis'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'error': 'Mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)
        if password != password2:
            return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response({'error': 'Mot de passe trop court (min 6)'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Ce nom d\'utilisateur existe déjà'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Cet email est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': profile.phone,
            'address': profile.address,
            'bio': profile.bio,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'message': 'Inscription réussie'
        }, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Identifiants requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if profile.two_factor_enabled:
            return Response({
                'two_factor_required': True,
                'user_id': user.id,
                'id': user.id,
                'username': user.username,
                'avatar_url': profile.avatar.url if profile.avatar else None,
                'message': 'Code 2FA requis'
            }, status=status.HTTP_200_OK)
        
        login(request, user)
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': profile.phone,
            'address': profile.address,
            'bio': profile.bio,
            'city': profile.city,
            'country': profile.country,
            'position': profile.position,
            'bank_name': profile.bank_name,
            'bank_account': profile.bank_account,
            'bank_code': profile.bank_code,
            'website': profile.website,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'is_authenticated': True,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff
        })

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Déconnexion réussie'})

@method_decorator(csrf_exempt, name='dispatch')
class MeView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            return Response({
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone': profile.phone,
                'address': profile.address,
                'bio': profile.bio,
                'city': profile.city,
                'country': profile.country,
                'position': profile.position,
                'bank_name': profile.bank_name,
                'bank_account': profile.bank_account,
                'bank_code': profile.bank_code,
                'website': profile.website,
                'avatar_url': profile.avatar.url if profile.avatar else None,
                'is_authenticated': True,
                'is_superuser': request.user.is_superuser,
                'is_staff': request.user.is_staff
            })
        return Response({'is_authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)

# ==================== VUE PROFIL ====================

class ProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id=None):
        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = request.user
            profile, created = UserProfile.objects.get_or_create(user=user)
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': profile.phone,
                'address': profile.address,
                'bio': profile.bio,
                'city': profile.city,
                'country': profile.country,
                'position': profile.position,
                'bank_name': profile.bank_name,
                'bank_account': profile.bank_account,
                'bank_code': profile.bank_code,
                'website': profile.website,
                'avatar_url': profile.avatar.url if profile.avatar else None,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff
            })
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class AvatarUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=user)
            if 'avatar' in request.FILES:
                if profile.avatar:
                    profile.avatar.delete()
                profile.avatar = request.FILES['avatar']
                profile.save()
                return Response({
                    'message': 'Avatar mis à jour avec succès',
                    'avatar_url': profile.avatar.url if profile.avatar else None
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Aucun fichier fourni'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================== MISE À JOUR COMPLÈTE DU PROFIL ====================

class UpdateProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def put(self, request):
        user_id = request.data.get('user_id')
        
        if not user_id:
            if request.user.is_authenticated:
                user_id = request.user.id
            else:
                return Response({'error': 'user_id requis'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        
        data = request.data
        
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.bio = data.get('bio', profile.bio)
        profile.city = data.get('city', profile.city)
        profile.country = data.get('country', profile.country)
        profile.position = data.get('position', profile.position)
        profile.bank_name = data.get('bank_name', profile.bank_name)
        profile.bank_account = data.get('bank_account', profile.bank_account)
        profile.bank_code = data.get('bank_code', profile.bank_code)
        profile.website = data.get('website', profile.website)
        profile.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': profile.phone,
            'address': profile.address,
            'bio': profile.bio,
            'city': profile.city,
            'country': profile.country,
            'position': profile.position,
            'bank_name': profile.bank_name,
            'bank_account': profile.bank_account,
            'bank_code': profile.bank_code,
            'website': profile.website,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'date_joined': user.date_joined,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'message': 'Profil mis à jour avec succès'
        }, status=200)

class UpdatePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(current_password):
            return Response({'error': 'Mot de passe actuel incorrect'}, status=400)
        
        if len(new_password) < 6:
            return Response({'error': 'Mot de passe trop court (min 6)'}, status=400)
        
        user.set_password(new_password)
        user.save()
        
        updated_user = authenticate(request, username=user.username, password=new_password)
        if updated_user:
            login(request, updated_user)
        
        return Response({'message': 'Mot de passe modifié avec succès'})

# ==================== VUES POUR LES UTILISATEURS ====================

@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({'error': 'Vous ne pouvez pas supprimer votre propre compte'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

# ==================== SAUVEGARDE ====================

class BackupDatabaseView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            recettes = list(Recette.objects.filter(statut='actif').values('id', 'date', 'montant', 'description', 'client', 'user'))
            depenses = list(Depense.objects.filter(statut='actif').values('id', 'date', 'montant', 'description', 'fournisseur', 'user'))
            clients = list(Client.objects.values('id', 'nom', 'telephone', 'email', 'adresse', 'user'))
            fournisseurs = list(Fournisseur.objects.values('id', 'nom', 'telephone', 'email', 'adresse', 'user'))
            
            data = {
                'recettes': recettes,
                'depenses': depenses,
                'clients': clients,
                'fournisseurs': fournisseurs,
                'export_date': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            json_data = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            
            # Enregistrer la sauvegarde en base de données
            try:
                # Récupérer l'utilisateur
                user = None
                if request.user.is_authenticated:
                    user = request.user
                else:
                    # Essayer de récupérer le premier admin
                    user = User.objects.filter(is_superuser=True).first()
                
                if user:
                    Backup.objects.create(
                        user=user,
                        filename=f"backup_logcompta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        size=len(json_data),
                        record_count=len(recettes) + len(depenses) + len(clients) + len(fournisseurs)
                    )
                    print(f"Sauvegarde enregistrée en base pour {user.username}")
                else:
                    print("Aucun utilisateur trouve pour la sauvegarde")
            except Exception as e:
                print(f"Erreur lors de l'enregistrement en base: {e}")
            
            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="backup_logcompta_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
            
        except Exception as e:
            print(f"Erreur generale: {e}")
            return Response({'error': str(e)}, status=500)

class ListBackupsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        backups = Backup.objects.all().order_by('-created_at')
        data = [{
            'id': b.id,
            'filename': b.filename,
            'size': f"{b.size / 1024:.2f} KB",
            'record_count': b.record_count,
            'created_at': b.created_at.strftime('%d/%m/%Y %H:%M:%S'),
            'user': {
                'id': b.user.id,
                'username': b.user.username,
                'email': b.user.email
            }
        } for b in backups]
        return Response(data)

class DeleteBackupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def delete(self, request, backup_id):
        try:
            backup = Backup.objects.get(id=backup_id)
            backup.delete()
            return Response({'message': 'Sauvegarde supprimee'})
        except Backup.DoesNotExist:
            return Response({'error': 'Sauvegarde non trouvee'}, status=404)

# ==================== RESTAURATION ====================

class RestoreDatabaseView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            backup_file = request.FILES.get('backup_file')
            if not backup_file:
                return Response({'error': 'Aucun fichier fourni'}, status=400)
            
            data = json.load(backup_file)
            
            if data.get('recettes') is None:
                return Response({'error': 'Fichier de sauvegarde invalide'}, status=400)
            
            # Restaurer les donnees
            for recette in data.get('recettes', []):
                Recette.objects.update_or_create(
                    id=recette.get('id'),
                    defaults={
                        'date': recette['date'],
                        'montant': recette['montant'],
                        'description': recette.get('description', ''),
                        'client_id': recette.get('client'),
                        'statut': recette.get('statut', 'actif'),
                        'user_id': recette.get('user')
                    }
                )
            
            for depense in data.get('depenses', []):
                Depense.objects.update_or_create(
                    id=depense.get('id'),
                    defaults={
                        'date': depense['date'],
                        'montant': depense['montant'],
                        'description': depense.get('description', ''),
                        'fournisseur_id': depense.get('fournisseur'),
                        'statut': depense.get('statut', 'actif'),
                        'user_id': depense.get('user')
                    }
                )
            
            for client in data.get('clients', []):
                Client.objects.update_or_create(
                    id=client.get('id'),
                    defaults={
                        'nom': client['nom'],
                        'telephone': client.get('telephone', ''),
                        'email': client.get('email', ''),
                        'adresse': client.get('adresse', ''),
                        'user_id': client.get('user')
                    }
                )
            
            for fournisseur in data.get('fournisseurs', []):
                Fournisseur.objects.update_or_create(
                    id=fournisseur.get('id'),
                    defaults={
                        'nom': fournisseur['nom'],
                        'telephone': fournisseur.get('telephone', ''),
                        'email': fournisseur.get('email', ''),
                        'adresse': fournisseur.get('adresse', ''),
                        'user_id': fournisseur.get('user')
                    }
                )
            
            return Response({
                'message': 'Restauration reussie',
                'count': len(data.get('recettes', [])) + len(data.get('depenses', [])) + len(data.get('clients', [])) + len(data.get('fournisseurs', []))
            }, status=200)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ==================== DOUBLE AUTHENTIFICATION ====================

import random
import string

@method_decorator(csrf_exempt, name='dispatch')
class EnableTwoFactorView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        code = request.data.get('code')
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id requis'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouve'}, status=404)
        
        if not code or len(code) != 6 or not code.isdigit():
            return Response({'error': 'Le code doit contenir 6 chiffres'}, status=400)
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.two_factor_enabled = True
        profile.two_factor_code = code
        profile.save()
        
        return Response({
            'two_factor_enabled': True, 
            'message': '2FA activee avec succes'
        })

@method_decorator(csrf_exempt, name='dispatch')
class DisableTwoFactorView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id requis'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouve'}, status=404)
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.two_factor_enabled = False
        profile.two_factor_code = ''
        profile.save()
        
        return Response({'message': '2FA desactivee'})

@method_decorator(csrf_exempt, name='dispatch')
class CheckTwoFactorStatusView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            return Response({'two_factor_enabled': profile.two_factor_enabled})
        
        user_id = request.GET.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                return Response({'two_factor_enabled': profile.two_factor_enabled})
            except User.DoesNotExist:
                pass
        
        return Response({'two_factor_enabled': False})

@method_decorator(csrf_exempt, name='dispatch')
class VerifyTwoFactorLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        code = request.data.get('code')
        user_id = request.data.get('user_id')
        
        if not user_id or not code:
            return Response({'error': 'Code et utilisateur requis'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouve'}, status=404)
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        if not profile.two_factor_enabled:
            return Response({'error': '2FA non activee'}, status=400)
        
        if profile.two_factor_code != code:
            return Response({'error': 'Code incorrect'}, status=400)
        
        login(request, user)
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'is_authenticated': True,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'message': 'Connexion reussie'
        })

# ==================== AUDIT LOG VIEW ====================

class AuditLogView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        entity_type = request.GET.get('entity_type')
        action = request.GET.get('action')
        user_id = request.GET.get('user_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        logs = AuditLog.objects.all()
        
        if entity_type:
            logs = logs.filter(entity_type=entity_type)
        if action:
            logs = logs.filter(action=action)
        if user_id:
            logs = logs.filter(user_id=user_id)
        if start_date:
            logs = logs.filter(created_at__date__gte=start_date)
        if end_date:
            logs = logs.filter(created_at__date__lte=end_date)
        
        data = [{
            'id': log.id,
            'user': {
                'id': log.user.id,
                'username': log.user.username,
                'first_name': log.user.first_name,
                'last_name': log.user.last_name,
            },
            'action': log.action,
            'action_display': dict(AuditLog.ACTION_TYPES).get(log.action, log.action),
            'entity_type': log.entity_type,
            'entity_type_display': dict(AuditLog.ENTITY_TYPES).get(log.entity_type, log.entity_type),
            'entity_id': log.entity_id,
            'entity_name': log.entity_name,
            'details': log.details,
            'created_at': log.created_at.strftime('%d/%m/%Y %H:%M:%S')
        } for log in logs]
        
        return Response(data)