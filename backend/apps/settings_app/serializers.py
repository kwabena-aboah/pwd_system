"""
settings_app/serializers.py
"""
from rest_framework import serializers
from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    logo_secondary_url = serializers.SerializerMethodField()

    class Meta:
        model = SystemSettings
        fields = '__all__'

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None

    def get_logo_secondary_url(self, obj):
        request = self.context.get('request')
        if obj.logo_secondary and request:
            return request.build_absolute_uri(obj.logo_secondary.url)
        return None
