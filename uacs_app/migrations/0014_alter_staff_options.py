# Generated by Django 4.2.3 on 2023-07-15 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uacs_app', '0013_alter_serviceprovider_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staff',
            options={'ordering': ['-created_date']},
        ),
    ]
