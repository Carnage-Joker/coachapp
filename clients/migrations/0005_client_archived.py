from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0004_enforce_client_user_not_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]

