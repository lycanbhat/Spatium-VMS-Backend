# Generated by Django 4.2 on 2024-03-25 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_active',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_archive',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, db_index=True, max_length=13, unique=True),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['email'], name='authenticat_email_486e08_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['phone_number'], name='authenticat_phone_n_226745_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['email', 'phone_number'], name='authenticat_email_c011e1_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(condition=models.Q(('is_archive', False)), fields=['is_archive'], name='unarchive_users_index'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.UniqueConstraint(fields=('email',), name='unique_email'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.UniqueConstraint(fields=('phone_number',), name='unique_phone_number'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.UniqueConstraint(fields=('email', 'phone_number'), name='unique_email_phone_number'),
        ),
    ]
