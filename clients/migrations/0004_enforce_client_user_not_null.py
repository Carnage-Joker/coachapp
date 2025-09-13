from django.db import migrations, models
from django.conf import settings


def assert_no_null_owners(apps, schema_editor):
    Client = apps.get_model('clients', 'Client')
    if Client.objects.filter(user__isnull=True).exists():
        raise RuntimeError(
            'Found Client rows with NULL user. Run backfill before migrating:\n'
            '  python manage.py backfill_client_owner --username <owner>\n'
            'or specify --user-id <id>.'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0003_client_user'),
    ]

    operations = [
        migrations.RunPython(assert_no_null_owners, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL),
        ),
    ]

