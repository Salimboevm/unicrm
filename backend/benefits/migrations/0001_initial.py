# Generated by Django 5.1.6 on 2025-03-18 15:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Benefit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('membership_level_required', models.CharField(choices=[('all', 'All Members'), ('community', 'Community Members'), ('key_access', 'Key Access Members'), ('creative_workspace', 'Creative Workspace Members')], default='all', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BenefitUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('usage_count', models.IntegerField(default=1)),
                ('notes', models.TextField(blank=True, null=True)),
                ('benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_records', to='benefits.benefit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='benefit_usage', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'benefit')},
            },
        ),
    ]
