# Generated by Django 2.2.7 on 2022-01-07 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0014_paymentdetail_uploaded_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='discount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='course',
            name='original_fee',
            field=models.FloatField(default=0),
        ),
    ]
