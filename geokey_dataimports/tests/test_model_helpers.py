# coding=utf-8
from cStringIO import StringIO
from django.test import TestCase


from geokey_dataimports.helpers.model_helpers import import_from_csv


class ImportFromCSVTest(TestCase):
    """Tests to check that characters can be imported from CSV files.

       Notes that these tests are probably not possible or relevant under Python 3.
    """
    def test_import_csv_basic_chars(self):
        """Basic ASCII characters can be imported."""
        input_dict = {u'abc': u'123', u'cde': u'456', u'efg': u'789'}
        mock_csv = StringIO("abc,cde,efg\n123,456,789")
        features = []
        import_from_csv(features=features, fields=[], file_obj=mock_csv)
        for k, v in input_dict.items():
            self.assertEquals(v, features[0]['properties'][k])

    def test_import_csv_non_ascii_chars(self):
        """Non-ASCII unicode characters can be imported."""
        input_dict = {u'à': u'¡', u'£': u'Ç'}
        mock_csv = StringIO("à,£\n¡,Ç")
        features = []
        import_from_csv(features=features, fields=[], file_obj=mock_csv)
        for k, v in input_dict.items():
            self.assertEquals(v, features[0]['properties'][k])

