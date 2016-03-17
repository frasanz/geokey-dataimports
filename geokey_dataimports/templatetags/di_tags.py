"""All template tags for the extension."""

from django import template


register = template.Library()


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
