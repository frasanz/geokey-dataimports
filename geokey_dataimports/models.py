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
        datafields = []
        datafeatures = []
        errors = []

        if instance.dataformat == FORMAT.KML:
            driver = ogr.GetDriverByName('KML')
            file = driver.Open(instance.file.path)

            for layer in file:
                for feature in layer:
                    datafeatures.append(feature.ExportToJson())
        else:
            csv.field_size_limit(sys.maxsize)
            file = open(instance.file.path, 'rU')

        if instance.dataformat == FORMAT.GeoJSON:
            reader = json.load(file)
            features = reader['features']

        if instance.dataformat == FORMAT.CSV:
            reader = csv.reader(file)

            for fieldname in next(reader, None):
                datafields.append({
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
                        current_datafield = datafields[i]
                        properties[current_datafield['name']] = column
                features.append({'line': line, 'properties': properties})

        for feature in datafeatures:
            geometries = {}

            for key, value in feature['properties'].iteritems():
                current_datafield = None

                for datafield in datafields:
                        if datafield['name'] == key:
                            current_datafield = datafield

                if current_datafield is None:
                    datafields.append({
                        'name': key,
                        'good_types': set(['TextField', 'LookupField']),
                        'bad_types': set([])
                    })
                    current_datafield = datafields[-1]

                fieldtype = None

                if 'geometry' not in feature:
                    try:
                        geometry = ogr.CreateGeometryFromWkt(str(value))
                        geometry = geometry.ExportToJson()
                    except:
                        geometry = None

                    fieldtype = 'GeometryField'
                    if geometry is not None:
                        if fieldtype not in current_datafield['bad_types']:
                            current_datafield['good_types'].add(fieldtype)
                            geometries[datafield['name']] = geometry
                    else:
                        current_datafield['good_types'].discard(fieldtype)
                        current_datafield['bad_types'].add(fieldtype)
                        fieldtype = None

                if fieldtype is None:
                    fieldtype = 'NumericField'
                    if type_helpers.is_numeric(value):
                        if fieldtype not in datafield['bad_types']:
                            datafield['good_types'].add(fieldtype)
                    else:
                        datafield['good_types'].discard(fieldtype)
                        datafield['bad_types'].add(fieldtype)

                    fieldtypes = ['DateField', 'DateTimeField']
                    if type_helpers.is_date(value):
                        for fieldtype in fieldtypes:
                            if fieldtype not in datafield['bad_types']:
                                datafield['good_types'].add(fieldtype)
                    else:
                        for fieldtype in fieldtypes:
                            datafield['good_types'].discard(fieldtype)
                            datafield['bad_types'].add(fieldtype)

                    fieldtype = 'TimeField'
                    if type_helpers.is_time(value):
                        if fieldtype not in datafield['bad_types']:
                            datafield['good_types'].add(fieldtype)
                    else:
                        datafield['good_types'].discard(fieldtype)
                        datafield['bad_types'].add(fieldtype)

            if 'geometry' not in feature and len(geometries) == 0:
                errors.append({
                    'line': feature['line'],
                    'messages': ['The entry has no geometry set.']
                })
                datafeatures['error'] = True
            else:
                datafeatures['geometries'] = geometries

        geometry_field = None
        for datafield in datafields:
            if 'GeometryField' not in datafield['good_types']:
                DataField.objects.create(
                    name=data_field['name'],
                    types=list(data_field['good_types']),
                    dataimport=instance
                )
            elif geometry_field is None:
                geometry_field = datafield['name']

        for datafeature in datafeatures:
            if 'geometry' in datafeature:
                geometry = datafeature['geometry']
            elif geometry_field in datafeature['geometries']:
                geometry = datafeature['geometries'][geometry_field]

            if geometry:
                DataFeature.objects.create(
                    geometry=geometry,
                    properties=datafeature['properties'],
                    dataimport=instance
                )


class DataField(TimeStampedModel):
    """Store a single data field."""

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    types = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    dataimport = models.ForeignKey(
        'DataImport',
        related_name='datafields'
    )

    def convert_to_field(self, name, key, field_type):
        """
        Convert data field to regular GeoKey field.

        Parameters
        ----------
        user : geokey.users.models.User
            The request user.
        name : str
            The name of the field.
        key : str
            The key of the field.
        field_type : str
            The field type.

        Returns
        -------
        geokey.categories.models.Field
            The field created.
        """
        category = self.dataimport.category

        proposed_key = key
        suggested_key = proposed_key

        count = 1
        while category.fields.filter(key=suggested_key).exists():
            suggested_key = '%s-%s' % (proposed_key, count)
            count += 1

        return Field.create(
            name,
            suggested_key,
            '', False,
            category,
            field_type
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
