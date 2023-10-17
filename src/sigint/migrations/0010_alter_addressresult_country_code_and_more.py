# Generated by Django 4.2.6 on 2023-10-17 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigint', '0009_alter_addressresult_continent_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressresult',
            name='country_code',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='addressresult',
            name='region_code',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
