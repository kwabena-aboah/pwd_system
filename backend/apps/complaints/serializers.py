"""
complaints/serializers.py
"""
from rest_framework import serializers
from .models import Complaint, ComplaintCategory, ComplaintNote


class ComplaintCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCategory
        fields = '__all__'


class ComplaintNoteSerializer(serializers.ModelSerializer):
    added_by_name = serializers.CharField(source='added_by.full_name', read_only=True)

    class Meta:
        model = ComplaintNote
        fields = '__all__'
        read_only_fields = ['added_by', 'created_at']


class ComplaintSerializer(serializers.ModelSerializer):
    pwd_name = serializers.CharField(source='pwd.full_name', read_only=True)
    pwd_reg = serializers.CharField(source='pwd.registration_number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    notes = ComplaintNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['complaint_number', 'created_by', 'resolved_by', 'resolved_at']
