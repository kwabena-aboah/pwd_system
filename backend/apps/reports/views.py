"""
reports/views.py
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='pwd-summary')
    def pwd_summary(self, request):
        from apps.pwds.models import PWD
        qs = PWD.objects.all()
        district = request.query_params.get('district')
        if district:
            qs = qs.filter(district=district)
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'by_gender': list(qs.values('gender').annotate(count=Count('id'))),
            'by_disability': list(
                qs.values('medical_records__disability_types__name')
                .annotate(count=Count('id')).order_by('-count')[:15]
            ),
            'by_district': list(qs.values('district').annotate(count=Count('id')).order_by('-count')),
            'by_education': list(qs.values('education_level').annotate(count=Count('id'))),
            'by_employment': list(qs.values('employment_status').annotate(count=Count('id'))),
            'by_age_group': _age_groups(qs),
        })

    @action(detail=False, methods=['get'], url_path='benefits-summary')
    def benefits_summary(self, request):
        from apps.benefits.models import BenefitAllocation
        qs = BenefitAllocation.objects.all()
        return Response({
            'total_allocations': qs.count(),
            'disbursed': qs.filter(status='disbursed').count(),
            'total_value_ghs': qs.filter(status='disbursed').aggregate(t=Sum('amount_disbursed'))['t'] or 0,
            'by_partner': list(
                qs.filter(status='disbursed')
                .values('benefit__partner__name')
                .annotate(count=Count('id'), total=Sum('amount_disbursed'))
                .order_by('-total')
            ),
            'by_category': list(
                qs.filter(status='disbursed')
                .values('benefit__category__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'pending': qs.filter(status='pending').count(),
        })

    @action(detail=False, methods=['get'], url_path='complaints-summary')
    def complaints_summary(self, request):
        from apps.benefits.models import Complaint
        qs = Complaint.objects.all()
        return Response({
            'total': qs.count(),
            'open': qs.filter(status='open').count(),
            'resolved': qs.filter(status='resolved').count(),
            'avg_resolution_days': _avg_resolution(qs),
            'by_priority': list(qs.values('priority').annotate(count=Count('id'))),
            'by_status': list(qs.values('status').annotate(count=Count('id'))),
        })


def _age_groups(qs):
    from datetime import date
    today = date.today()
    groups = [
        ('0-17', 0, 17), ('18-35', 18, 35), ('36-50', 36, 50),
        ('51-65', 51, 65), ('66+', 66, 200),
    ]
    result = []
    for label, min_age, max_age in groups:
        min_dob = today.replace(year=today.year - max_age - 1)
        max_dob = today.replace(year=today.year - min_age)
        count = qs.filter(date_of_birth__gte=min_dob, date_of_birth__lte=max_dob).count()
        result.append({'age_group': label, 'count': count})
    return result


def _avg_resolution(qs):
    resolved = qs.filter(status='resolved', resolved_at__isnull=False)
    total_days = 0
    count = 0
    for c in resolved:
        delta = (c.resolved_at.date() - c.date_lodged).days
        total_days += delta
        count += 1
    return round(total_days / count, 1) if count else 0
