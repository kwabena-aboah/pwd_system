"""
apps/notifications/signals.py — Auto-notify on key events
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.pwds.models import PWD
from apps.benefits.models import BenefitAllocation
from apps.settings_app.models import Notification, SystemSettings

User = get_user_model()


def create_notification(recipient, ntype, title, message, link=''):
    Notification.objects.create(
        recipient=recipient,
        notification_type=ntype,
        title=title,
        message=message,
        link=link,
    )


def notify_admins(ntype, title, message, link=''):
    """Send notification to all super admins and district officers."""
    admins = User.objects.filter(
        role__in=['super_admin', 'district_officer'],
        is_active=True
    )
    for admin in admins:
        create_notification(admin, ntype, title, message, link)


@receiver(post_save, sender=PWD)
def notify_new_pwd(sender, instance, created, **kwargs):
    if created:
        settings = SystemSettings.get_settings()
        if settings.notify_new_pwd:
            notify_admins(
                'new_pwd',
                f'New PWD Registered: {instance.full_name}',
                f'{instance.registration_number} has been registered in {instance.district}.',
                f'/pwds/{instance.pk}'
            )


@receiver(post_save, sender=BenefitAllocation)
def notify_benefit_update(sender, instance, created, **kwargs):
    settings = SystemSettings.get_settings()
    if not settings.notify_benefit_approval:
        return
    if created:
        notify_admins(
            'benefit',
            f'New Benefit Allocation Pending',
            f'{instance.pwd.full_name} — {instance.benefit.name} awaiting approval.',
            f'/allocations'
        )
    elif instance.status == 'disbursed':
        # Notify the person who recorded it
        if instance.recorded_by:
            create_notification(
                instance.recorded_by,
                'benefit',
                'Benefit Disbursed',
                f'{instance.benefit.name} has been disbursed to {instance.pwd.full_name}.',
                f'/allocations'
            )
