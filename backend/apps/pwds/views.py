"""
pwds/views.py — ViewSets with AI, export, and filtering
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db.models import Count, Q
from .models import PWD, MedicalRecord, DisabilityType, PWDDocument
from .serializers import (
    PWDListSerializer, PWDDetailSerializer,
    MedicalRecordSerializer, DisabilityTypeSerializer, PWDDocumentSerializer
)
from apps.accounts.models import Role
import openai


class IsEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.can_edit


class DisabilityTypeViewSet(viewsets.ModelViewSet):
    queryset = DisabilityType.objects.all()
    serializer_class = DisabilityTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class PWDViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEditorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'gender', 'district', 'region', 'ai_risk_label',
                        'employment_status', 'education_level']
    search_fields = ['first_name', 'last_name', 'registration_number',
                     'national_id', 'community', 'phone']

    def get_queryset(self):
        qs = PWD.objects.select_related('registered_by').prefetch_related(
            'medical_records__disability_types', 'documents'
        )
        # Partners see limited data
        user = self.request.user
        if user.role in [Role.NGO_PARTNER, Role.GOVT_OFFICER]:
            qs = qs.filter(district=user.district)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PWDListSerializer
        return PWDDetailSerializer

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='generate-ai-summary')
    def generate_ai_summary(self, request, pk=None):
        """Generate AI profile summary and risk assessment"""
        pwd = self.get_object()
        med = pwd.medical_records.first()

        prompt = f"""
        Analyze this PWD profile and provide:
        1. A brief 2-sentence professional summary
        2. A vulnerability risk score (0-100)
        3. Risk label: low/medium/high/critical
        4. 3 concrete intervention recommendations

        Profile:
        - Name: {pwd.full_name}, Age: {pwd.age}, Gender: {pwd.gender}
        - Community: {pwd.community}, District: {pwd.district}
        - Employment: {pwd.employment_status}, Income: GHS {pwd.monthly_income or 0}/month
        - Household size: {pwd.household_size}
        - Health insurance: {pwd.has_nhis if hasattr(pwd, 'has_nhis') else 'Unknown'}
        - Disability: {med.disability_types.values_list('name', flat=True) if med else 'Not recorded'}
        - Severity: {med.disability_severity if med else 'Unknown'}
        - Assistive device: {med.has_assistive_device if med else 'Unknown'}
        - Benefits received: {pwd.benefit_allocations.filter(status='disbursed').count()}
        - Open complaints: {pwd.complaints.filter(status__in=['open', 'in_progress']).count()}

        Respond in JSON: {{
            "summary": "...",
            "risk_score": 0-100,
            "risk_label": "low|medium|high|critical",
            "recommendations": ["...", "...", "..."]
        }}
        """

        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            import json
            data = json.loads(resp.choices[0].message.content)
            pwd.ai_summary = data.get('summary', '')
            pwd.ai_risk_score = data.get('risk_score')
            pwd.ai_risk_label = data.get('risk_label', '')
            pwd.ai_recommendations = '\n'.join(data.get('recommendations', []))
            pwd.save(update_fields=['ai_summary', 'ai_risk_score', 'ai_risk_label', 'ai_recommendations'])
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Dashboard stats for charts"""
        qs = self.get_queryset()
        total = qs.count()

        by_gender = list(qs.values('gender').annotate(count=Count('id')))
        by_status = list(qs.values('status').annotate(count=Count('id')))
        by_district = list(qs.values('district').annotate(count=Count('id')).order_by('-count')[:10])
        by_risk = list(qs.values('ai_risk_label').annotate(count=Count('id')))
        by_employment = list(qs.values('employment_status').annotate(count=Count('id')))

        # Disability type breakdown
        from apps.pwds.models import DisabilityType
        disability_counts = []
        for dt in DisabilityType.objects.all():
            count = qs.filter(medical_records__disability_types=dt).count()
            if count:
                disability_counts.append({'name': dt.name, 'count': count})

        # Monthly registrations (last 12 months)
        from django.db.models.functions import TruncMonth
        from datetime import date
        monthly = list(
            qs.annotate(month=TruncMonth('registration_date'))
            .values('month').annotate(count=Count('id'))
            .order_by('month').values('month', 'count')
        )

        return Response({
            'total': total,
            'active': qs.filter(status='active').count(),
            'high_risk': qs.filter(ai_risk_label__in=['high', 'critical']).count(),
            'by_gender': by_gender,
            'by_status': by_status,
            'by_district': by_district,
            'by_risk': by_risk,
            'by_employment': by_employment,
            'by_disability_type': disability_counts,
            'monthly_registrations': monthly,
        })

    @action(detail=False, methods=['get'], url_path='album')
    def album(self, request):
        """Album endpoint — filtered, paginated list for printing"""
        qs = self.get_queryset().filter(status='active')
        district = request.query_params.get('district')
        if district:
            qs = qs.filter(district=district)
        serializer = PWDListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.select_related('pwd').prefetch_related('disability_types')
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsEditorOrReadOnly]
    filterset_fields = ['pwd', 'disability_severity', 'disability_onset']

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
