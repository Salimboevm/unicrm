# Generated by Django 5.1.6 on 2025-04-10 16:16

import django.db.models.deletion
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
                ('category', models.CharField(max_length=100)),
                ('membership_group', models.CharField(choices=[('community', 'Community Member'), ('key_access', 'Key Access Member'), ('creative_workspace', 'Creative Workspace Member'), ('all', 'All Members')], default='all', help_text='The membership group that can access this benefit', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('requires_activation', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBenefit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('activated_on', models.DateTimeField(blank=True, null=True)),
                ('expires_on', models.DateTimeField(blank=True, null=True)),
                ('benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benefits.benefit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_benefits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'benefit')},
            },
        ),
        migrations.CreateModel(
            name='BenefitUsageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('logged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logged_benefits', to=settings.AUTH_USER_MODEL)),
                ('user_benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_logs', to='benefits.userbenefit')),
            ],
        ),
    ]
