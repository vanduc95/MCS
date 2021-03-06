# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-23 11:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('identifier', models.CharField(max_length=255, null=True, verbose_name='identifier')),
                ('status', models.IntegerField(blank=True, choices=[(1, 'UPDATE'), (2, 'NOT_UPDATE'), (3, 'AVAILABLE'), (4, 'NOT_AVAILABLE')], default=3, null=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True, verbose_name='last_modified')),
                ('path', models.CharField(max_length=255, null=True, verbose_name='path')),
                ('content', models.FileField(null=True, upload_to=b'', verbose_name='content')),
                ('is_folder', models.BooleanField(default=True, verbose_name='is_folder')),
                ('is_root', models.BooleanField(default=False, verbose_name='is_root')),
                ('size', models.IntegerField(editable=False, null=True, verbose_name='size')),
                ('size_format', models.CharField(max_length=255, null=True, verbose_name='size_format')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dashboard.File', verbose_name='parent')),
            ],
            options={
                'db_table': 'file',
            },
        ),
    ]
