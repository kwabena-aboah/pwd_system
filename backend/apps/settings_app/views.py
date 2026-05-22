"""
settings_app/views.py
"""
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import action
from .models import SystemSettings
from .serializers import SystemSettingsSerializer


class SystemSettingsView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        settings = SystemSettings.get_settings()
        serializer = SystemSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        settings = SystemSettings.get_settings()
        serializer = SystemSettingsSerializer(
            settings, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# Audit Log ViewSet
# ─────────────────────────────────────────────────────────────────────────────
from rest_framework import viewsets, filters
from auditlog.models import LogEntry
from django_filters.rest_framework import DjangoFilterBackend


class AuditLogSerializer:
    pass  # handled inline below


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['actor__email', 'actor__first_name', 'object_repr']
    filterset_fields = ['action', 'content_type__model']
    ordering = ['-timestamp']
    ordering_fields = ['timestamp', 'action']

    def get_queryset(self):
        user = self.request.user
        if user.role not in ['super_admin', 'auditor']:
            return LogEntry.objects.none()
        return LogEntry.objects.select_related('actor', 'content_type').all()

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            data = self._serialize(page)
            return self.get_paginated_response(data)
        return Response(self._serialize(qs))

    def _serialize(self, logs):
        return [{
            'id': log.id,
            'timestamp': log.timestamp,
            'actor': log.actor.get_full_name() if log.actor else 'System',
            'actor_email': log.actor.email if log.actor else '',
            'action': log.get_action_display(),
            'model': log.content_type.model if log.content_type else '',
            'object': log.object_repr,
            'changes': log.changes_dict,
            'remote_addr': log.remote_addr,
        } for log in logs]
