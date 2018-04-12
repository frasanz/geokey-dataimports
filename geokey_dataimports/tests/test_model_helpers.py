# coding=utf-8
from io import BytesIO
from django.test import TestCase


from geokey_dataimports.helpers.model_helpers import import_from_csv


class ImportFromCSVTest(TestCase):
    """Tests to check that characters can be imported from CSV files.

       Notes that these tests are probably not possible or relevant under Python 3.
    """
    def test_import_csv_basic_chars(self):
        """Basic ASCII characters can be imported."""
        mock_csv = BytesIO("abc,cde,efg\n123,456,789")
        features = []
        import_from_csv(features=features, fields=[], file=mock_csv)
        print(features)
        self.assertEquals(features[0]['properties'], {'cde': '456', 'abc': '123', 'efg': '789'})

    def test_import_csv_non_ascii_chars(self):
        """Non-ASCII unicode characters can be imported."""
        mock_csv = BytesIO("abc,àde,e£g\n¡23,45Ç,Æ8é")
        features = []
        import_from_csv(features=features, fields=[], file=mock_csv)
        print(features)
        self.assertEquals(features[0]['properties'], {'àde': '45Ç', 'abc': '¡23', 'e£g': 'Æ8é'})
