"""Base for the extension."""

from model_utils import Choices


STATUS = Choices('active', 'deleted')
FORMAT = Choices('GeoJSON', 'KML', 'CSV')
