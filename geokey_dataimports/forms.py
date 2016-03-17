"""All forms for the extension."""

from django.forms import ModelForm

from geokey.categories.models import Category

from .models import DataImport


class CategoryForm(ModelForm):
    """Form for a single category."""

    class Meta:
        """Form meta."""

        model = Category
        fields = ('name', 'description')


class DataImportForm(ModelForm):
    """Form for a single data import."""

    class Meta:
        """Form meta."""

        model = DataImport
        fields = ('name', 'description', 'file')
