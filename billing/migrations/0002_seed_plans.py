from django.db import migrations

def seed_plans(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')
    
    # Company Plans
    Plan.objects.get_or_create(
        name="Company Growth",
        tenant_type="COMPANY",
        price_per_month_inr=2999.00,
        max_active_job_postings=5,
        max_students=None,
        is_active=True
    )
    Plan.objects.get_or_create(
        name="Company Enterprise",
        tenant_type="COMPANY",
        price_per_month_inr=9999.00,
        max_active_job_postings=None,
        max_students=None,
        is_active=True
    )

    # College Plans
    Plan.objects.get_or_create(
        name="College Basic",
        tenant_type="COLLEGE",
        price_per_month_inr=9999.00,
        max_active_job_postings=None,
        max_students=500,
        is_active=True
    )
    Plan.objects.get_or_create(
        name="College Enterprise",
        tenant_type="COLLEGE",
        price_per_month_inr=24999.00,
        max_active_job_postings=None,
        max_students=None,
        is_active=True
    )

def remove_plans(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')
    Plan.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_plans, reverse_code=remove_plans),
    ]
