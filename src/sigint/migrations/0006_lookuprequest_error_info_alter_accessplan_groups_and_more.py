# Generated by Django 4.2.6 on 2023-10-17 03:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('sigint', '0005_alter_geosync_asn_file_alter_geosync_city_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lookuprequest',
            name='error_info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='accessplan',
            name='groups',
            field=models.ManyToManyField(blank=True, to='auth.group'),
        ),
        migrations.AlterField(
            model_name='accessplan',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
