"""
management/commands/create_initial_data.py
Seeds the database with disability types, benefit categories, complaint categories and system settings.
"""
from django.core.management.base import BaseCommand
from apps.pwds.models import DisabilityType
from apps.benefits.models import BenefitCategory
from apps.complaints.models import ComplaintCategory
from apps.settings_app.models import SystemSettings


class Command(BaseCommand):
    help = 'Seed initial data for PWD system'

    def handle(self, *args, **options):
        self.stdout.write('Seeding disability types...')
        disability_types = [
            ('Physical Disability', 'PHY', 'physical'),
            ('Visual Impairment', 'VIS', 'sensory'),
            ('Hearing Impairment', 'HEA', 'sensory'),
            ('Speech Impairment', 'SPE', 'sensory'),
            ('Intellectual Disability', 'INT', 'intellectual'),
            ('Psychosocial Disability', 'PSY', 'psychosocial'),
            ('Autism Spectrum Disorder', 'AUT', 'intellectual'),
            ('Multiple Disabilities', 'MUL', 'multiple'),
            ('Albinism', 'ALB', 'sensory'),
            ('Dwarfism', 'DWA', 'physical'),
            ('Cerebral Palsy', 'CEP', 'physical'),
            ('Epilepsy', 'EPI', 'psychosocial'),
        ]
        for name, code, category in disability_types:
            DisabilityType.objects.get_or_create(
                code=code,
                defaults={'name': name, 'category': category}
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(disability_types)} disability types'))

        self.stdout.write('Seeding benefit categories...')
        categories = [
            ('Cash Transfer', 'Cash-based financial support'),
            ('Assistive Devices', 'Wheelchairs, crutches, hearing aids, etc.'),
            ('Education Support', 'School fees, uniforms, books'),
            ('Medical Support', 'Hospital fees, medications, therapy'),
            ('Vocational Training', 'Skills training and livelihood support'),
            ('Food Support', 'Food baskets and nutrition programmes'),
            ('Housing Support', 'Shelter improvement and construction'),
            ('Legal Aid', 'Legal representation and advocacy'),
            ('Psychosocial Support', 'Counselling and mental health services'),
            ('Social Inclusion', 'Community activities and integration'),
        ]
        for name, desc in categories:
            BenefitCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(categories)} benefit categories'))

        self.stdout.write('Seeding complaint categories...')
        complaint_cats = [
            'Benefit Not Received',
            'Benefit Amount Wrong',
            'Discrimination',
            'Abuse / Neglect',
            'Staff Misconduct',
            'Data Entry Error',
            'Service Denial',
            'Inaccessible Facilities',
            'Transport Barrier',
            'Other',
        ]
        for name in complaint_cats:
            ComplaintCategory.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(complaint_cats)} complaint categories'))

        self.stdout.write('Creating system settings...')
        SystemSettings.get_settings()
        self.stdout.write(self.style.SUCCESS('  ✓ System settings initialised'))

        self.stdout.write(self.style.SUCCESS('\n✅ Initial data seeded successfully!'))
        self.stdout.write('Run: python manage.py createsuperuser to create your admin account.')
