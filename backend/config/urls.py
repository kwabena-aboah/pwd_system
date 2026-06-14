"""
config/urls.py
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,  # Correct name
)

from apps.pwds.views import PWDViewSet, MedicalRecordViewSet, DisabilityTypeViewSet
from apps.accounts.views import UserViewSet, AuthViewSet
from apps.benefits.views import BenefitViewSet, BenefitAllocationViewSet, DevelopmentPartnerViewSet, BenefitCategoryViewSet
from apps.complaints.views import ComplaintViewSet, ComplaintCategoryViewSet
from apps.notifications.views import NotificationViewSet
from apps.reports.views import ReportViewSet
from apps.settings_app.views import SystemSettingsView, AuditLogViewSet
from apps.subscriptions.views import (PlanViewSet, SubscriptionViewSet,
    InvoiceViewSet, PaystackWebhookView)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('pwds', PWDViewSet, basename='pwd')
router.register('medical-records', MedicalRecordViewSet, basename='medical-record')
router.register('disability-types', DisabilityTypeViewSet, basename='disability-type')
router.register('partners', DevelopmentPartnerViewSet, basename='partner')
router.register('benefit-categories', BenefitCategoryViewSet, basename='benefit-category')
router.register('benefits', BenefitViewSet, basename='benefit')
router.register('benefit-allocations', BenefitAllocationViewSet, basename='benefit-allocation')
router.register('complaint-categories', ComplaintCategoryViewSet, basename='complaint-category')
router.register('complaints', ComplaintViewSet, basename='complaint')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('reports', ReportViewSet, basename='report')
router.register('audit-logs', AuditLogViewSet, basename='audit-log')
router.register('plans', PlanViewSet, basename='plan')
router.register('subscriptions', SubscriptionViewSet, basename='subscription')
router.register('invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/settings/', SystemSettingsView.as_view(), name='system-settings'),
    path('api/webhooks/paystack/', PaystackWebhookView.as_view(), name='paystack-webhook'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
