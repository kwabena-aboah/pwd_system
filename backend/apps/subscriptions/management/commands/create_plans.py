"""management/commands/create_plans.py — seed default subscription plans"""
from django.core.management.base import BaseCommand
from apps.subscriptions.models import Plan


PLANS = [
    {
        'name': 'Free Trial', 'tier': 'free', 'sort_order': 0,
        'description': 'Explore the system with no commitment.',
        'price_monthly': 0, 'price_yearly': 0,
        'max_users': 3, 'max_pwds': 50, 'max_partners': 2,
        'max_districts': 1, 'storage_gb': 1,
        'trial_days': 14,
        'feature_ai': False, 'feature_album_pdf': True, 'feature_album_pptx': False,
        'feature_audit': False, 'feature_reports': False, 'feature_api_access': False,
        'feature_white_label': False, 'feature_bulk_import': False,
        'feature_offline': True, 'feature_support': 'community',
    },
    {
        'name': 'Starter', 'tier': 'starter', 'sort_order': 1,
        'description': 'Perfect for small district offices getting started.',
        'price_monthly': 199, 'price_yearly': 1990,
        'max_users': 5, 'max_pwds': 300, 'max_partners': 5,
        'max_districts': 1, 'storage_gb': 5,
        'trial_days': 14,
        'feature_ai': False, 'feature_album_pdf': True, 'feature_album_pptx': True,
        'feature_audit': False, 'feature_reports': True, 'feature_api_access': False,
        'feature_white_label': False, 'feature_bulk_import': False,
        'feature_offline': True, 'feature_support': 'email',
    },
    {
        'name': 'Standard', 'tier': 'standard', 'sort_order': 2, 'is_popular': True,
        'description': 'Most popular. Full features for a single district.',
        'price_monthly': 399, 'price_yearly': 3990,
        'max_users': 15, 'max_pwds': 1000, 'max_partners': 20,
        'max_districts': 1, 'storage_gb': 20,
        'trial_days': 14,
        'feature_ai': True, 'feature_album_pdf': True, 'feature_album_pptx': True,
        'feature_audit': True, 'feature_reports': True, 'feature_api_access': False,
        'feature_white_label': True, 'feature_bulk_import': True,
        'feature_offline': True, 'feature_support': 'priority',
    },
    {
        'name': 'Professional', 'tier': 'professional', 'sort_order': 3,
        'description': 'Multi-district operations with full AI and API access.',
        'price_monthly': 799, 'price_yearly': 7990,
        'max_users': 50, 'max_pwds': 5000, 'max_partners': 0,
        'max_districts': 5, 'storage_gb': 100,
        'trial_days': 14,
        'feature_ai': True, 'feature_album_pdf': True, 'feature_album_pptx': True,
        'feature_audit': True, 'feature_reports': True, 'feature_api_access': True,
        'feature_white_label': True, 'feature_bulk_import': True,
        'feature_offline': True, 'feature_support': 'priority',
    },
    {
        'name': 'Enterprise', 'tier': 'enterprise', 'sort_order': 4,
        'description': 'Region-wide deployment with dedicated support and SLA.',
        'price_monthly': 0, 'price_yearly': 0,  # custom pricing
        'max_users': 0, 'max_pwds': 0, 'max_partners': 0,
        'max_districts': 0, 'storage_gb': 500,
        'trial_days': 30,
        'feature_ai': True, 'feature_album_pdf': True, 'feature_album_pptx': True,
        'feature_audit': True, 'feature_reports': True, 'feature_api_access': True,
        'feature_white_label': True, 'feature_bulk_import': True,
        'feature_offline': True, 'feature_support': 'dedicated',
    },
]


class Command(BaseCommand):
    help = 'Seed default subscription plans'

    def handle(self, *args, **options):
        for data in PLANS:
            plan, created = Plan.objects.update_or_create(
                tier=data['tier'],
                defaults=data,
            )
            verb = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: {plan.name}'))
        self.stdout.write(self.style.SUCCESS('\n✅ Plans seeded successfully!'))
