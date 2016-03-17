"""All tests for template tags."""

from django.test import TestCase

from .model_factories import DataFeatureFactory
from ..templatetags import di_tags


class SubtractTest(TestCase):
    """Test subtract filter."""

    def test_filter(self):
        """Test filter."""
        self.assertEqual(di_tags.subtract(10, 3), 7)


class FilterImportedTest(TestCase):
    """Test filter_imported filter."""

    def test_filter(self):
        """Test filter."""
        datafeature_1 = DataFeatureFactory.create(imported=True)
        datafeature_2 = DataFeatureFactory.create(imported=True)
        datafeatures = [datafeature_1, datafeature_2]

        self.assertEqual(
            di_tags.filter_imported(datafeatures),
            [datafeature_1]
        )
