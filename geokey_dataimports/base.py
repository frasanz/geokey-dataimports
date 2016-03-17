"""Base for the extension."""

from model_utils import Choices


STATUS = Choices('active', 'invalid', 'deleted')
FORMAT = Choices('GeoJSON', 'KML', 'CSV')
