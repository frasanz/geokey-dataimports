# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geokey_dataimports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafield',
            name='key',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
