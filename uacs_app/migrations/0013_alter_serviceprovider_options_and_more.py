# Generated by Django 4.2.3 on 2023-07-15 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uacs_app', '0012_alter_serviceprovider_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serviceprovider',
            options={},
        ),
        migrations.AddIndex(
            model_name='serviceprovider',
            index=models.Index(fields=['name'], name='uacs_app_se_name_2ce0ba_idx'),
        ),
        migrations.AddIndex(
            model_name='staff',
            index=models.Index(fields=['first_name', 'last_name'], name='uacs_app_st_first_n_918d1a_idx'),
        ),
    ]
