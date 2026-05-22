# notifications/models.py — Notification model lives in settings_app to avoid circular imports
from apps.settings_app.models import Notification
__all__ = ['Notification']
