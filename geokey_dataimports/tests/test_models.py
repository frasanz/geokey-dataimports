"""All tests for models."""

import os

from django.test import TestCase

from nose.tools import raises

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.models import Category
from geokey.categories.tests.model_factories import CategoryFactory

from .model_factories import DataImportFactory
from ..models import DataImport, post_save_project, post_save_category


class DataImportTest(TestCase):
    """Test data import model."""

    def setUp(self):
        """Set up test."""
        self.file = None

    def tearDown(self):
        """Tear down test."""
        if self.file:
            os.remove(self.file)

    @raises(DataImport.DoesNotExist)
    def test_delete(self):
        """Test delete data import."""
        dataimport = DataImportFactory.create()
        self.file = dataimport.file.path
        dataimport.delete()
        DataImport.objects.get(pk=dataimport.id)


class PostSaveProjectTest(TestCase):
    """Test post save for project."""

    def setUp(self):
        """Set up test."""
        self.file = None

    def tearDown(self):
        """Tear down test."""
        if self.file:
            os.remove(self.file)

    @raises(DataImport.DoesNotExist)
    def test_post_save_project_when_deleting(self):
        """
        Test delete project.

        Data imports should also be removed.
        """
        project = ProjectFactory.create(status='active')
        dataimport = DataImportFactory.create(project=project)
        self.file = dataimport.file.path
        project.delete()

        post_save_project(Project, instance=project)

        DataImport.objects.get(pk=dataimport.id)


class PostSaveCategoryTest(TestCase):
    """Test post save for category."""

    def setUp(self):
        """Set up test."""
        self.file = None

    def tearDown(self):
        """Tear down test."""
        if self.file:
            os.remove(self.file)

    @raises(DataImport.DoesNotExist)
    def test_post_save_category_when_deleting(self):
        """
        Test delete category.

        Data imports should also be removed.
        """
        category = CategoryFactory.create(status='active')
        dataimport = DataImportFactory.create(category=category)
        self.file = dataimport.file.path
        category.delete()

        post_save_category(Category, instance=category)

        DataImport.objects.get(pk=dataimport.id)
