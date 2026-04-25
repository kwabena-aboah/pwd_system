"""
benefits/serializers.py
"""
from rest_framework import serializers
from .models import DevelopmentPartner, BenefitCategory, Benefit, BenefitAllocation


class DevelopmentPartnerSerializer(serializers.ModelSerializer):
    benefit_count = serializers.SerializerMethodField()

    class Meta:
        model = DevelopmentPartner
        fields = '__all__'

    def get_benefit_count(self, obj):
        return obj.benefits.count()


class BenefitCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitCategory
        fields = '__all__'


class BenefitSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    allocation_count = serializers.SerializerMethodField()

    class Meta:
        model = Benefit
        fields = '__all__'
        read_only_fields = ['created_by']

    def get_allocation_count(self, obj):
        return obj.allocations.count()


class BenefitAllocationSerializer(serializers.ModelSerializer):
    pwd_name = serializers.CharField(source='pwd.full_name', read_only=True)
    pwd_reg = serializers.CharField(source='pwd.registration_number', read_only=True)
    benefit_name = serializers.CharField(source='benefit.name', read_only=True)
    partner_name = serializers.CharField(source='benefit.partner.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)

    class Meta:
        model = BenefitAllocation
        fields = '__all__'
        read_only_fields = ['recorded_by', 'approved_by', 'approval_date']
