"""
notifications/serializers.py
"""
from rest_framework import serializers
from apps.settings_app.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['recipient', 'created_at']
