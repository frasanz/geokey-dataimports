"""All tests for template tags."""

from django.test import TestCase

from .model_factories import DataImportFactory, DataFeatureFactory
from ..models import DataFeature
from ..templatetags import di_tags


class ToClassNameTest(TestCase):
    """Test to_class_name filter."""

    def test_filter(self):
        """Test filter."""
        self.assertEqual(
            di_tags.to_class_name(DataFeatureFactory.create()),
            'DataFeature'
        )


class SubtractTest(TestCase):
    """Test subtract filter."""

    def test_filter(self):
        """Test filter."""
        self.assertEqual(di_tags.subtract(10, 3), 7)


class FilterImportedTest(TestCase):
    """Test filter_imported filter."""

    def test_filter(self):
        """Test filter."""
        dataimport = DataImportFactory.create()
        DataFeatureFactory.create(imported=True, dataimport=dataimport)
        DataFeatureFactory.create(imported=True, dataimport=dataimport)
        DataFeatureFactory.create(imported=False, dataimport=dataimport)
        datafeatures = DataFeature.objects.filter(dataimport=dataimport)

        self.assertEqual(len(di_tags.filter_imported(datafeatures)), 2)
