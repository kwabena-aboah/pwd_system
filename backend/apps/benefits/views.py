"""
benefits/views.py
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import DevelopmentPartner, BenefitCategory, Benefit, BenefitAllocation
from .serializers import (
    DevelopmentPartnerSerializer, BenefitCategorySerializer,
    BenefitSerializer, BenefitAllocationSerializer
)
from django.utils import timezone


class DevelopmentPartnerViewSet(viewsets.ModelViewSet):
    queryset = DevelopmentPartner.objects.all()
    serializer_class = DevelopmentPartnerSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'acronym', 'contact_person']
    filterset_fields = ['partner_type', 'is_active', 'district', 'region']


class BenefitCategoryViewSet(viewsets.ModelViewSet):
    queryset = BenefitCategory.objects.all()
    serializer_class = BenefitCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class BenefitViewSet(viewsets.ModelViewSet):
    queryset = Benefit.objects.select_related('partner', 'category').all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['partner', 'category', 'status', 'frequency']
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        from django.db.models import Sum, Count
        allocations = BenefitAllocation.objects.filter(status='disbursed')
        return Response({
            'total_disbursed': allocations.aggregate(total=Sum('amount_disbursed'))['total'] or 0,
            'disbursed_count': allocations.count(),
            'by_partner': list(
                allocations.values('benefit__partner__name')
                .annotate(count=Count('id'), total=Sum('amount_disbursed'))
                .order_by('-total')[:10]
            ),
            'by_category': list(
                allocations.values('benefit__category__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
            'pending_approvals': BenefitAllocation.objects.filter(status='pending').count(),
        })


class BenefitAllocationViewSet(viewsets.ModelViewSet):
    queryset = BenefitAllocation.objects.select_related('pwd', 'benefit', 'benefit__partner').all()
    serializer_class = BenefitAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'pwd', 'benefit', 'benefit__partner']
    search_fields = ['pwd__first_name', 'pwd__last_name', 'pwd__registration_number']

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        alloc = self.get_object()
        if not request.user.can_approve_benefits:
            return Response({'error': 'Insufficient permission'}, status=403)
        alloc.status = 'approved'
        alloc.approved_by = request.user
        alloc.approval_date = timezone.now()
        alloc.save()
        return Response(BenefitAllocationSerializer(alloc).data)

    @action(detail=True, methods=['post'], url_path='disburse')
    def disburse(self, request, pk=None):
        alloc = self.get_object()
        if not request.user.can_approve_benefits:
            return Response({'error': 'Insufficient permission'}, status=403)
        alloc.status = 'disbursed'
        alloc.disbursement_date = timezone.now().date()
        alloc.save()
        return Response(BenefitAllocationSerializer(alloc).data)
