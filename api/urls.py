from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecetteViewSet, DepenseViewSet, 
    ClientViewSet, FournisseurViewSet,
    RegisterView, LoginView, LogoutView, MeView,
    UserViewSet, ProfileView, BackupDatabaseView, 
    ListBackupsView, DeleteBackupView, AvatarUploadView,
    UpdateProfileView, UpdatePasswordView,
    EnableTwoFactorView, DisableTwoFactorView, CheckTwoFactorStatusView, VerifyTwoFactorLoginView,
    AuditLogView, RestoreDatabaseView
)

router = DefaultRouter()
router.register(r'recettes', RecetteViewSet)
router.register(r'depenses', DepenseViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'fournisseurs', FournisseurViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>/avatar/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('update-password/', UpdatePasswordView.as_view(), name='update_password'),
    path('backup/', BackupDatabaseView.as_view(), name='backup'),
    path('backups/list/', ListBackupsView.as_view(), name='backups_list'),
    path('backups/<int:backup_id>/delete/', DeleteBackupView.as_view(), name='backup_delete'),
    path('restore/', RestoreDatabaseView.as_view(), name='restore'),
    # Routes 2FA
    path('2fa/enable/', EnableTwoFactorView.as_view(), name='2fa_enable'),
    path('2fa/disable/', DisableTwoFactorView.as_view(), name='2fa_disable'),
    path('2fa/status/', CheckTwoFactorStatusView.as_view(), name='2fa_status'),
    path('2fa/verify-login/', VerifyTwoFactorLoginView.as_view(), name='2fa_verify_login'),
    # Audit Log
    path('audit-logs/', AuditLogView.as_view(), name='audit_logs'),
]