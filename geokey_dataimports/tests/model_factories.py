"""All model factories for tests."""

import factory

from django.core.files import File

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from .helpers import file_helpers
from ..base import STATUS
from ..models import DataImport, DataField, DataFeature


class DataImportFactory(factory.django.DjangoModelFactory):
    """Fake a single data import."""

    status = STATUS.active

    name = factory.Sequence(lambda n: 'Data import %s' % n)
    description = factory.LazyAttribute(lambda o: '%s description.' % o.name)
    dataformat = 'CSV'
    file = File(open(file_helpers.get_csv_file().name))

    project = factory.SubFactory(ProjectFactory)
    category = factory.SubFactory(CategoryFactory)
    creator = factory.SubFactory(UserFactory)

    class Meta:
        """Model factory meta."""

        model = DataImport


class DataFieldFactory(factory.django.DjangoModelFactory):
    """Fake a single data field."""

    key = factory.Sequence(lambda n: 'field-%s' % n)
    types = ['TextField']

    dataimport = factory.SubFactory(DataImportFactory)

    class Meta:
        """Model factory meta."""

        model = DataField


class DataFeatureFactory(factory.django.DjangoModelFactory):
    """Fake a single data feature."""

    imported = False
    geometry = 'POINT(-0.134040713310241 51.52447878755655)'
    properties = {}

    dataimport = factory.SubFactory(DataImportFactory)

    class Meta:
        """Model factory meta."""

        model = DataFeature
