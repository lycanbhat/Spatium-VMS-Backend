# Generated by Django 4.2 on 2024-04-22 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0005_purposeofvisit'),
        ('vms', '0002_alter_visitor_email_alter_visitor_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitor',
            name='purpose_of_visit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purpose_if_visit', to='admin_panel.purposeofvisit'),
        ),
    ]
