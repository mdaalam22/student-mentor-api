# Generated by Django 3.2.9 on 2021-12-10 16:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_auto_20211210_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrolled',
            name='enrolled_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
