"""
pwds/serializers.py
"""
from rest_framework import serializers
from .models import PWD, MedicalRecord, DisabilityType, PWDDocument


class DisabilityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisabilityType
        fields = '__all__'


class PWDDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)

    class Meta:
        model = PWDDocument
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    disability_types = DisabilityTypeSerializer(many=True, read_only=True)
    disability_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=DisabilityType.objects.all(), many=True,
        write_only=True, source='disability_types'
    )

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['recorded_by']


class PWDListSerializer(serializers.ModelSerializer):
    """Lightweight — for lists and album"""
    age = serializers.ReadOnlyField()
    disability_summary = serializers.SerializerMethodField()

    class Meta:
        model = PWD
        fields = [
            'id', 'pwd_id', 'registration_number', 'photo',
            'first_name', 'last_name', 'other_names',
            'age', 'gender', 'community', 'district', 'region',
            'status', 'ai_risk_label', 'disability_summary',
            'registration_date',
        ]

    def get_disability_summary(self, obj):
        med = obj.medical_records.first()
        if med:
            types = med.disability_types.values_list('name', flat=True)
            return ', '.join(types)
        return ''


class PWDDetailSerializer(serializers.ModelSerializer):
    """Full detail with nested medical records"""
    age = serializers.ReadOnlyField()
    medical_records = MedicalRecordSerializer(many=True, read_only=True)
    documents = PWDDocumentSerializer(many=True, read_only=True)
    registered_by_name = serializers.CharField(source='registered_by.full_name', read_only=True)
    benefit_count = serializers.SerializerMethodField()
    complaint_count = serializers.SerializerMethodField()

    class Meta:
        model = PWD
        fields = '__all__'
        read_only_fields = [
            'pwd_id', 'registration_number', 'registered_by',
            'ai_risk_score', 'ai_risk_label', 'ai_summary',
            'ai_recommendations', 'created_at', 'updated_at',
        ]

    def get_benefit_count(self, obj):
        return obj.benefit_allocations.filter(status='disbursed').count()

    def get_complaint_count(self, obj):
        return obj.complaints.count()
