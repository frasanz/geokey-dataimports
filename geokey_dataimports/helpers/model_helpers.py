import csv
import codecs

from django.utils.html import strip_tags
from six import PY3


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


def import_from_csv(features, fields, file_obj):
    if PY3:
        reader = csv.reader(file_obj)
    else:
        reader = UnicodeReader(file_obj)
    for fieldname in next(reader, None):
        fields.append({
            'name': strip_tags(fieldname),
            'good_types': {'TextField', 'LookupField'},
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
