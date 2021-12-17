# Generated by Django 3.2.9 on 2021-12-10 05:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0005_enrolled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrolled',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_course', to='course.course'),
        ),
        migrations.AlterField(
            model_name='enrolled',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
