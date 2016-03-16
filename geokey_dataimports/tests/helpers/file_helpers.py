"""All helpers for the file mocks."""

import csv


def get_csv_file(fieldnames=['ID', 'Geometry', 'Name', 'Short Description']):
    """
    Get CSV file.

    It adds three entries for default field names.

    Parameters
    ----------
    fieldnames : list
        Names for fields to write to the header of a file.

    Returns
    -------
    FILE
        Generated CSV file.
    """
    with open('test_csv.csv', 'wb') as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()

        csv_writer.writerow({
            'ID': 1,
            'Geometry': 'POINT (30 10)',
            'Name': 'Meat',
            'Short Description': 'Meat is good.'
        })
        csv_writer.writerow({
            'ID': 2,
            'Geometry': 'LINESTRING (30 10, 10 30, 40 40)',
            'Name': 'Fish',
            'Short Description': 'Fish is healthy.'
        })
        csv_writer.writerow({
            'ID': 3,
            'Geometry': 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))',
            'Name': 'Vegetables',
            'Short Description': 'Vegetables are even healthier.'
        })

    return file
