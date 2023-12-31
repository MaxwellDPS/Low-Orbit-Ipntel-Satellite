# Generated by Django 4.2.6 on 2023-10-16 04:00

import django.core.files.storage.filesystem
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigint', '0004_alter_geosync_asn_file_alter_geosync_city_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geosync',
            name='asn_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.filesystem.FileSystemStorage, upload_to='asn'),
        ),
        migrations.AlterField(
            model_name='geosync',
            name='city_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.filesystem.FileSystemStorage, upload_to='city'),
        ),
        migrations.AlterField(
            model_name='geosync',
            name='country_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.filesystem.FileSystemStorage, upload_to='country'),
        ),
    ]
