from django.contrib import admin
from .models import Recette, Depense, Client, Fournisseur

@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'montant', 'description', 'created_at')
    list_filter = ('date',)
    search_fields = ('description',)

@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'montant', 'description', 'created_at')
    list_filter = ('date',)
    search_fields = ('description',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'telephone', 'adresse')
    search_fields = ('nom', 'telephone')

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'telephone', 'adresse')
    search_fields = ('nom', 'telephone')