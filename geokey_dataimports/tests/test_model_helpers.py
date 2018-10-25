# coding=utf-8
from django.test import TestCase
from six import PY2, BytesIO, StringIO


from geokey_dataimports.helpers.model_helpers import import_from_csv


class MockCSV(object):

    def __init__(self, text):
        self.text = text
        self.index = 0

    def next(self):
        try:
            next_item = self.text[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return str(next_item)

    def __next__(self):
        return self.next()

    def __iter__(self):
        return self


class ImportFromCSVTest(TestCase):
    """Tests to check that characters can be imported from CSV files.

       Notes that these tests are probably not possible or relevant under Python 3.
    """
    def test_import_csv_basic_chars(self):
        """Basic ASCII characters can be imported."""
        input_dict = {'abc': '123', 'cde': '456', 'efg': '789'}
        if PY2:
            mock_csv = BytesIO(b"abc,cde,efg\n123,456,789")
        else:
            mock_csv = StringIO("abc,cde,efg\n123,456,789")
        features = []
        import_from_csv(features=features, fields=[], file_obj=mock_csv)
        for k, v in input_dict.items():
            self.assertEquals(v, features[0]['properties'][k])

    def test_import_csv_non_ascii_chars(self):
        """Non-ASCII unicode characters can be imported."""
        input_dict = {u'à': u'¡', u'£': u'Ç'}
        if PY2:
            mock_csv = BytesIO("à,£\n¡,Ç")
        else:
            mock_csv = StringIO("à,£\n¡,Ç")
        features = []
        import_from_csv(features=features, fields=[], file_obj=mock_csv)
        for k, v in input_dict.items():
            self.assertEquals(v, features[0]['properties'][k])

