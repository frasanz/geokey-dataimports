"""All managers for the extension."""

from django.db import models

from .base import STATUS


class DataImportManager(models.Manager):
    """Manage a single data import."""

    def get_queryset(self):
        """
        Return all data imports.

        Returns
        -------
        django.db.models.Queryset
            All imports, excluding deleted.
        """
        return super(
            DataImportManager,
            self
        ).get_queryset().exclude(status=STATUS.deleted)
