# Generated by Django 4.2 on 2024-03-27 05:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0001_initial'),
        ('authentication', '0004_remove_customuser_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='company_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_company', to='admin_panel.company'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AddField(
            model_name='otpmodel',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
