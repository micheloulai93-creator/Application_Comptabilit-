from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recette, Depense, Client, Fournisseur, UserProfile

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'

class RecetteSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    
    class Meta:
        model = Recette
        fields = '__all__'

class DepenseSerializer(serializers.ModelSerializer):
    fournisseur_nom = serializers.CharField(source='fournisseur.nom', read_only=True)
    
    class Meta:
        model = Depense
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'bio', 'avatar', 'avatar_url')
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'is_superuser', 'is_staff', 'date_joined', 'profile', 'avatar_url', 'role')
    
    def get_avatar_url(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url
        return None
    
    def get_role(self, obj):
        if obj.is_superuser:
            return 'super_admin'
        elif obj.is_staff:
            return 'admin'
        return 'comptable'