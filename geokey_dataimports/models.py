"""All models for the extension."""

import sys
import json
import csv

from osgeo import ogr

from django.conf import settings
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db import models
from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField
from model_utils.models import StatusModel, TimeStampedModel

from geokey.projects.models import Project
from geokey.categories.models import Category

from .helpers import type_helpers
from .base import STATUS, FORMAT
from .managers import DataImportManager


class DataImport(StatusModel, TimeStampedModel):
    """Store a single data import."""

    STATUS = STATUS
    FORMAT = FORMAT

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    dataformat = models.CharField(max_length=10, null=False, choices=FORMAT)
    file = models.FileField(
        upload_to='dataimports/files',
        max_length=500
    )

    project = models.ForeignKey(
        'projects.Project',
        related_name='dataimports'
    )
    category = models.ForeignKey(
        'categories.Category',
        null=True,
        blank=True
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = DataImportManager()

    def delete(self, *args, **kwargs):
        """Delete the data import by setting its status to `deleted`."""
        self.status = self.STATUS.deleted
        self.save()

    def get_lookup_fields(self):
        """Get all lookup fields of a category."""
        lookupfields = {}
        for field in self.category.fields.all():
            if field.fieldtype == 'LookupField':
                lookupfields[field.key] = field
        return lookupfields

    def import_contributions(self, user, ids):
        """
        Convert data features to contributions.

        Parameters
        ----------
        user : geokey.users.models.User
            The request user.
        ids : list
            The list of IDs of data features to be imported.

        Returns
        -------
        list
            The list of error messages, containing dicts of data feature IDs
            and messages.
        """
        from geokey.contributions.serializers import ContributionSerializer

        data_features = self.datafeatures.filter(id__in=ids, imported=False)
        lookupfields = self.get_lookup_fields()
        errors = []

        for data_feature in data_features:
            properties = data_feature.properties

            for key, value in properties.iteritems():
                if key in lookupfields:
                    lookupfield = lookupfields[key]
                    lookupvalue = lookupfield.lookupvalues.get(name=value)
                    properties[key] = lookupvalue.id

            feature = {
                "location": {
                    "geometry": data_feature.geometry
                },
                "meta": {
                    "category": self.category.id,
                },
                "properties": properties
            }

            serializer = ContributionSerializer(
                data=feature,
                context={'user': user, 'project': self.project}
            )

            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                data_feature.imported = True
                data_feature.save()
            except ValidationError, error:
                errors.append({
                    'id': data_feature.id,
                    'messages': error.messages
                })

        return errors


@receiver(models.signals.post_save, sender=DataImport)
def post_save_dataimport(sender, instance, created, **kwargs):
    """Map data fields and data features when the data import gets created."""
    if created:
        csv.field_size_limit(sys.maxsize)
        file = open(instance.file.path, 'rU')

        data_fields = []
        data_features = []
        errors = []

        if instance.dataformat == FORMAT.GeoJSON:
            reader = json.load(file)

            if reader['type'] != 'FeatureCollection' or not reader['features']:
                print 'Not a valid GeoJSON FeatureCollection.'

            for feature in reader['features']:
                for key, value in feature['properties'].iteritems():
                    print value
        elif instance.dataformat == FORMAT.CSV:
            reader = csv.reader(file)
            keys = set([])

            for field_name in next(reader, None):
                field_name = strip_tags(field_name)

                if field_name:
                    proposed_key = slugify(field_name)
                    suggested_key = proposed_key

                    count = 1
                    while suggested_key in keys:
                        suggested_key = '%s-%s' % (proposed_key, count)
                        count += 1
                    keys.add(suggested_key)

                    data_fields.append({
                        'name': field_name,
                        'key': suggested_key,
                        'good_types': set(['TextField', 'LookupField']),
                        'bad_types': set([])
                    })

            line = 0
            for row in reader:
                line += 1
                geometries = {}
                properties = {}

                for i, column in enumerate(row):
                    if column:
                        data_field = data_fields[i]

                        try:
                            geometry = ogr.CreateGeometryFromWkt(str(column))
                            geometry = geometry.ExportToJson()
                        except:
                            geometry = None

                        field_type = 'GeometryField'
                        if geometry is not None:
                            if field_type not in data_field['bad_types']:
                                data_field['good_types'].add(field_type)
                                geometries[data_field['key']] = geometry
                        else:
                            data_field['good_types'].discard(field_type)
                            data_field['bad_types'].add(field_type)

                            field_type = 'NumericField'
                            if type_helpers.is_numeric(column):
                                if field_type not in data_field['bad_types']:
                                    data_field['good_types'].add(field_type)
                            else:
                                data_field['good_types'].discard(field_type)
                                data_field['bad_types'].add(field_type)

                            field_types = ['DateField', 'DateTimeField']
                            if type_helpers.is_date(column):
                                for field_type in field_types:
                                    if (field_type not in
                                            data_field['bad_types']):
                                        data_field['good_types'].add(
                                            field_type)
                            else:
                                for field_type in field_types:
                                    data_field['good_types'].discard(
                                        field_type)
                                    data_field['bad_types'].add(
                                        field_type)

                            field_type = 'TimeField'
                            if type_helpers.is_time(column):
                                if field_type not in data_field['bad_types']:
                                    data_field['good_types'].add(field_type)
                            else:
                                data_field['good_types'].discard(field_type)
                                data_field['bad_types'].add(field_type)

                            properties[data_field['key']] = column

                if len(geometries) == 0:
                    errors.append({
                        'line': line,
                        'messages': ['The entry has no geometry set.']
                    })
                else:
                    data_features.append({
                        'line': line,
                        'geometries': geometries,
                        'properties': properties
                    })

        geometry_field_key = None
        for data_field in data_fields:
            if 'GeometryField' not in data_field['good_types']:
                DataField.objects.create(
                    name=data_field['name'],
                    key=data_field['key'],
                    types=list(data_field['good_types']),
                    dataimport=instance
                )
            elif geometry_field_key is None:
                geometry_field_key = data_field['key']

        for data_feature in data_features:
            if geometry_field_key in data_feature['geometries']:
                DataFeature.objects.create(
                    geometry=data_feature['geometries'][geometry_field_key],
                    properties=data_feature['properties'],
                    dataimport=instance
                )
            else:
                errors.append({
                    'line': data_feature['line'],
                    'messages': [
                        'Entry has no geometry set inside the `%s column.' % (
                            geometry_field_key
                        )
                    ]
                })


class DataField(TimeStampedModel):
    """Store a single data field."""

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    types = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    dataimport = models.ForeignKey(
        'DataImport',
        related_name='datafields'
    )


class DataFeature(TimeStampedModel):
    """Store a single data feature."""

    imported = models.BooleanField(default=False)
    geometry = gis.GeometryField(geography=True)
    properties = JsonBField(default={})

    dataimport = models.ForeignKey(
        'DataImport',
        related_name='datafeatures'
    )


@receiver(models.signals.post_save, sender=Project)
def post_save_project(sender, instance, **kwargs):
    """Remove associated data imports when the project gets deleted."""
    if instance.status == 'deleted':
        DataImport.objects.filter(project=instance).delete()


@receiver(models.signals.post_save, sender=Category)
def post_save_category(sender, instance, **kwargs):
    """Remove associated data imports when the category gets deleted."""
    if instance.status == 'deleted':
        DataImport.objects.filter(category=instance).delete()
