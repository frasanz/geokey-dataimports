"""All models for the extension."""

import sys
import json
import csv

from osgeo import ogr

from django.conf import settings
from django.dispatch import receiver
from django.db import models
from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField
from model_utils.models import StatusModel, TimeStampedModel

from geokey.projects.models import Project
from geokey.categories.models import Category, Field

from .helpers import type_helpers
from .base import STATUS, FORMAT
from .exceptions import FileParseError
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
    keys = ArrayField(models.CharField(max_length=100), null=True, blank=True)

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


@receiver(models.signals.post_save, sender=DataImport)
def post_save_dataimport(sender, instance, created, **kwargs):
    """Map data fields and data features when the data import gets created."""
    if created:
        datafields = []
        datafeatures = []

        fields = []
        features = []
        errors = []

        if instance.dataformat == FORMAT.KML:
            driver = ogr.GetDriverByName('KML')
            reader = driver.Open(instance.file.path)

            for layer in reader:
                for feature in layer:
                    features.append(feature.ExportToJson())
        else:
            csv.field_size_limit(sys.maxsize)
            file = open(instance.file.path, 'rU')

        if instance.dataformat == FORMAT.GeoJSON:
            reader = json.load(file)
            features = reader['features']

        if instance.dataformat == FORMAT.CSV:
            reader = csv.reader(file)

            for fieldname in next(reader, None):
                fields.append({
                    'name': strip_tags(fieldname),
                    'good_types': set(['TextField', 'LookupField']),
                    'bad_types': set([])
                })

            line = 0
            for row in reader:
                line += 1
                properties = {}

                for i, column in enumerate(row):
                    if column:
                        field = fields[i]
                        properties[field['name']] = column

                features.append({'line': line, 'properties': properties})

        for feature in features:
            geometries = {}

            for key, value in feature['properties'].iteritems():
                field = None

                for existing_field in fields:
                    if existing_field['name'] == key:
                        field = existing_field
                        break

                if field is None:
                    fields.append({
                        'name': key,
                        'good_types': set(['TextField', 'LookupField']),
                        'bad_types': set([])
                    })
                    field = fields[-1]

                fieldtype = None

                if 'geometry' not in feature:
                    try:
                        geometry = ogr.CreateGeometryFromWkt(str(value))
                        geometry = geometry.ExportToJson()
                    except:
                        geometry = None

                    fieldtype = 'GeometryField'
                    if geometry is not None:
                        if fieldtype not in field['bad_types']:
                            field['good_types'].add(fieldtype)
                            geometries[field['name']] = json.loads(geometry)
                    else:
                        field['good_types'].discard(fieldtype)
                        field['bad_types'].add(fieldtype)
                        fieldtype = None

                if fieldtype is None:
                    fieldtype = 'NumericField'
                    if type_helpers.is_numeric(value):
                        if fieldtype not in field['bad_types']:
                            field['good_types'].add(fieldtype)
                    else:
                        field['good_types'].discard(fieldtype)
                        field['bad_types'].add(fieldtype)

                    fieldtypes = ['DateField', 'DateTimeField']
                    if type_helpers.is_date(value):
                        for fieldtype in fieldtypes:
                            if fieldtype not in field['bad_types']:
                                field['good_types'].add(fieldtype)
                    else:
                        for fieldtype in fieldtypes:
                            field['good_types'].discard(fieldtype)
                            field['bad_types'].add(fieldtype)

                    fieldtype = 'TimeField'
                    if type_helpers.is_time(value):
                        if fieldtype not in field['bad_types']:
                            field['good_types'].add(fieldtype)
                    else:
                        field['good_types'].discard(fieldtype)
                        field['bad_types'].add(fieldtype)

            if 'geometry' not in feature and len(geometries) == 0:
                errors.append({
                    'line': feature['line'],
                    'messages': ['The entry has no geometry set.']
                })
            else:
                feature['geometries'] = geometries

        geometryfield = None
        for field in fields:
            if 'GeometryField' not in field['good_types']:
                datafields.append({
                    'name': field['name'],
                    'types': list(field['good_types'])
                })
            elif geometryfield is None:
                geometryfield = field['name']

        for feature in features:
            geometry = None
            if 'geometry' in feature:
                geometry = feature['geometry']
            elif 'geometries' in feature:
                if not geometryfield:
                    errors.append({
                        'line': feature['line'],
                        'messages': ['The file has no valid geometry field.']
                    })
                else:
                    geometries = feature['geometries']
                    if geometryfield in geometries:
                        geometry = geometries[geometryfield]

            if geometry:
                datafeatures.append({
                    'geometry': geometry,
                    'properties': feature['properties']
                })

        if errors:
            instance.delete()
            raise FileParseError('Failed to read file.', errors)
        else:
            for datafield in datafields:
                if datafield['name']:
                    DataField.objects.create(
                        name=datafield['name'],
                        types=list(datafield['types']),
                        dataimport=instance
                    )
            for datafeature in datafeatures:
                DataFeature.objects.create(
                    geometry=json.dumps(datafeature['geometry']),
                    properties=datafeature['properties'],
                    dataimport=instance
                )


class DataField(TimeStampedModel):
    """Store a single data field."""

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, null=True, blank=True)
    types = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    dataimport = models.ForeignKey(
        'DataImport',
        related_name='datafields'
    )

    def convert_to_field(self, name, fieldtype):
        """
        Convert data field to regular GeoKey field.

        Parameters
        ----------
        user : geokey.users.models.User
            The request user.
        name : str
            The name of the field.
        fieldtype : str
            The field type.

        Returns
        -------
        geokey.categories.models.Field
            The field created.
        """
        category = self.dataimport.category
        field = None

        if self.key:
            try:
                field = category.fields.get(key=self.key)
            except Category.DoesNotExist:
                pass

        proposed_key = slugify(self.name)
        suggested_key = proposed_key

        if field:
            suggested_key = field.key
        else:
            count = 1
            while category.fields.filter(key=suggested_key).exists():
                suggested_key = '%s-%s' % (proposed_key, count)
                count += 1

            self.key = suggested_key
            self.save()

            field = Field.create(
                name,
                self.key,
                '', False,
                category,
                fieldtype
            )

        if self.key != self.name:
            for datafeature in self.dataimport.datafeatures.all():
                properties = datafeature.properties
                if self.name in properties:
                    properties[self.key] = properties.pop(self.name)
                datafeature.properties = properties
                datafeature.save()

        return field


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
