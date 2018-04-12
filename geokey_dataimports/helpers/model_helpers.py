import csv

from django.utils.html import strip_tags


def import_from_csv(features, fields, file):
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
