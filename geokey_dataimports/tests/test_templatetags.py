"""All tests for template tags."""

from django.test import TestCase

from .model_factories import DataImportFactory, DataFeatureFactory
from ..models import DataImport, DataFeature
from ..templatetags import di_tags


class ToClassNameTest(TestCase):
    """Test to_class_name filter."""

    def tearDown(self):
        """Tear down test."""
        for dataimport in DataImport.objects.all():
            if dataimport.file:
                dataimport.file.delete()

    def test_filter(self):
        """Test filter."""
        self.assertEqual(
            di_tags.to_class_name(DataImportFactory.create()),
            'DataImport'
        )
        self.assertEqual(
            di_tags.to_class_name(DataFeatureFactory.create()),
            'DataFeature'
        )


class ToFieldNameTest(TestCase):
    """Test to_field_name filter."""

    def test_filter(self):
        """Test filter."""
        self.assertEqual(
            di_tags.to_field_name('TextField'), 'Text'
        )
        self.assertEqual(
            di_tags.to_field_name('NumericField'), 'Numeric'
        )
        self.assertEqual(
            di_tags.to_field_name('DateTimeField'), 'Date and Time'
        )
        self.assertEqual(
            di_tags.to_field_name('DateField'), 'Date'
        )
        self.assertEqual(
            di_tags.to_field_name('TimeField'), 'Time'
        )
        self.assertEqual(
            di_tags.to_field_name('LookupField'), 'Select box'
        )
        self.assertEqual(
            di_tags.to_field_name('MultipleLookupField'), 'Multiple select'
        )
        self.assertEqual(
            di_tags.to_field_name('NonExistingField'), 'NonExistingField'
        )


class SubtractTest(TestCase):
    """Test subtract filter."""

    def test_filter(self):
        """Test filter."""
        self.assertEqual(di_tags.subtract(10, 3), 7)


class FilterImportedTest(TestCase):
    """Test filter_imported filter."""

    def tearDown(self):
        """Tear down test."""
        for dataimport in DataImport.objects.all():
            if dataimport.file:
                dataimport.file.delete()

    def test_filter(self):
        """Test filter."""
        dataimport = DataImportFactory.create()
        DataFeatureFactory.create(imported=True, dataimport=dataimport)
        DataFeatureFactory.create(imported=True, dataimport=dataimport)
        DataFeatureFactory.create(imported=False, dataimport=dataimport)
        datafeatures = DataFeature.objects.filter(dataimport=dataimport)

        self.assertEqual(len(di_tags.filter_imported(datafeatures)), 2)
