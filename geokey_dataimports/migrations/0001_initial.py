# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import model_utils.fields
import django_pgjson.fields
import django.contrib.postgres.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('categories', '0016_multiplelookupvalue_symbol'),
        ('projects', '0007_auto_20160122_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFeature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('imported', models.BooleanField(default=False)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
                ('properties', django_pgjson.fields.JsonBField(default={})),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('types', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=100), blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('status', model_utils.fields.StatusField(default=b'active', max_length=100, verbose_name='status', no_check_for_status=True, choices=[(b'active', b'active'), (b'invalid', b'invalid'), (b'deleted', b'deleted')])),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, verbose_name='status changed', monitor='status')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('dataformat', models.CharField(max_length=10, choices=[(b'GeoJSON', b'GeoJSON'), (b'KML', b'KML'), (b'CSV', b'CSV')])),
                ('file', models.FileField(max_length=500, upload_to=b'dataimports/files')),
                ('keys', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=100), blank=True)),
                ('category', models.ForeignKey(blank=True, to='categories.Category', null=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='dataimports', to='projects.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='datafield',
            name='dataimport',
            field=models.ForeignKey(related_name='datafields', to='geokey_dataimports.DataImport'),
        ),
        migrations.AddField(
            model_name='datafeature',
            name='dataimport',
            field=models.ForeignKey(related_name='datafeatures', to='geokey_dataimports.DataImport'),
        ),
    ]
