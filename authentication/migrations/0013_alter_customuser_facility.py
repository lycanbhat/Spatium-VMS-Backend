# Generated by Django 4.2 on 2024-04-12 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0004_company_facility'),
        ('authentication', '0012_customuser_facility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='facility',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_facility', to='admin_panel.facility'),
        ),
    ]
