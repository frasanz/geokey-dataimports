"""All template tags for the extension."""

from django import template


register = template.Library()


@register.filter
def to_class_name(object):
    """
    Return class name of an object.

    Parameters
    ----------
    object : obj
        An object.

    Returns
    -------
    str
        A class name of an object.
    """
    return object.__class__.__name__


@register.filter
def to_field_name(name):
    """
    Return a human readable field name (used on GeoKey).

    Parameters
    ----------
    name : str
        Field class name.

    Returns
    -------
    str
        Human readable field name.
    """
    fields = {
        'TextField': 'Text',
        'NumericField': 'Numeric',
        'DateTimeField': 'Date and Time',
        'DateField': 'Date',
        'TimeField': 'Time',
        'LookupField': 'Select box',
        'MultipleLookupField': 'Multiple select'
    }

    if name in fields:
        name = fields[name]

    return name


@register.filter
def subtract(minuend, subtrahend):
    """
    Subtract subtrahend from minuend.

    Parameters
    ----------
    minuend : int
        Minuend.
    subtrahend : int
        Subtrahend

    Returns
    -------
    int
        Difference.
    """
    return minuend - subtrahend


@register.filter
def filter_imported(datafeatures):
    """
    Filter imported data features.

    Parameters
    ----------
    datafeatures : geokey_dataimport.models.DataFeature
        A set of data features to be filtered.

    Returns
    -------
    geokey_dataimport.models.DataFeature
        Filtered dataset.
    """
    return datafeatures.filter(imported=True)
