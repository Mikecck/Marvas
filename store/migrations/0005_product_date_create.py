# Generated by Django 2.2 on 2022-01-21 21:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20201203_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]