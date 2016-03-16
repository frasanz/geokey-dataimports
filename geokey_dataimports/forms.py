"""All forms for the extension."""

from django.forms import ModelForm

from .models import DataImport


class DataImportForm(ModelForm):
    """Form for a single data import."""

    class Meta:
        """Form meta."""

        model = DataImport
        fields = ('name', 'description', 'file')
