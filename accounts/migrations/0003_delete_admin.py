# Generated by Django 4.2.3 on 2023-07-05 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_admin_designation_admin_role_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Admin',
        ),
    ]
