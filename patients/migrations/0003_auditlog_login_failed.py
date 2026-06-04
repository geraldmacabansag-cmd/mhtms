from django.db import migrations
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_patient_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='action',
            field=django.db.models.fields.CharField(
                choices=[
                    ('create', 'Created'),
                    ('edit', 'Edited'),
                    ('status_change', 'Status Changed'),
                    ('discharge', 'Discharged'),
                    ('view', 'Viewed'),
                    ('login', 'Login'),
                    ('login_failed', 'Failed Login'),
                    ('logout', 'Logout'),
                ],
                max_length=30,
            ),
        ),
    ]
