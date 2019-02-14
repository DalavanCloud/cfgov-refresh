# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-14 08:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0135_relatedresource'),
        ('ask_cfpb', '0018_answerpage_redirect_to_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answerpage',
            name='next_step',
        ),
        migrations.AddField(
            model_name='answerpage',
            name='related_resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='v1.RelatedResource'),
        ),
    ]
