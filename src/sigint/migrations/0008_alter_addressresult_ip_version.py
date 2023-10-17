# Generated by Django 4.2.6 on 2023-10-17 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigint', '0007_alter_addressresult_lookup_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressresult',
            name='ip_version',
            field=models.CharField(blank=True, choices=[('4', 'IPv4'), ('6', 'IPv6')], db_index=True, max_length=255, null=True, verbose_name='IP Version'),
        ),
    ]