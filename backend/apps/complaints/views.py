"""
complaints/views.py
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Complaint, ComplaintCategory, ComplaintNote
from .serializers import ComplaintSerializer, ComplaintCategorySerializer, ComplaintNoteSerializer


class ComplaintCategoryViewSet(viewsets.ModelViewSet):
    queryset = ComplaintCategory.objects.all()
    serializer_class = ComplaintCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.select_related('pwd', 'assigned_to', 'category').all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to', 'source']
    search_fields = ['title', 'description', 'complaint_number', 'pwd__first_name', 'pwd__last_name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        complaint = self.get_object()
        user_id = request.data.get('user_id')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            complaint.assigned_to = user
            complaint.status = 'in_progress'
            complaint.save()
            return Response(ComplaintSerializer(complaint).data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        complaint.status = 'resolved'
        complaint.resolution = request.data.get('resolution', '')
        complaint.resolved_by = request.user
        complaint.resolved_at = timezone.now()
        complaint.save()
        return Response(ComplaintSerializer(complaint).data)

    @action(detail=True, methods=['post'], url_path='add-note')
    def add_note(self, request, pk=None):
        complaint = self.get_object()
        note = ComplaintNote.objects.create(
            complaint=complaint,
            note=request.data.get('note', ''),
            added_by=request.user
        )
        return Response(ComplaintNoteSerializer(note).data)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        from django.db.models import Count
        qs = Complaint.objects.all()
        return Response({
            'total': qs.count(),
            'open': qs.filter(status='open').count(),
            'in_progress': qs.filter(status='in_progress').count(),
            'resolved': qs.filter(status='resolved').count(),
            'by_priority': list(qs.values('priority').annotate(count=Count('id'))),
            'by_category': list(
                qs.values('category__name').annotate(count=Count('id')).order_by('-count')[:10]
            ),
        })
