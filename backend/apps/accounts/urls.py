from django.urls import path
from .views import AuthViewSet, UserViewSet

urlpatterns = [
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('me/update/', UserViewSet.as_view({'patch': 'update_me'}), name='update-me'),
    path('change-password/', AuthViewSet.as_view({'post': 'change_password'}), name='change-password'),
]
