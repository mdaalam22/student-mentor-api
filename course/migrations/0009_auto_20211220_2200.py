# Generated by Django 3.2.9 on 2021-12-20 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_auto_20211217_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrolled',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='can_view',
            field=models.BooleanField(default=False),
        ),
    ]
