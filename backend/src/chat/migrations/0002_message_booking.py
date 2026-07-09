from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0004_driverlocation'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='booking',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='messages',
                to='trip.booking',
            ),
        ),
    ]
