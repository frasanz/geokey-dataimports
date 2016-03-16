"""All tests for URLs."""

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import (
    IndexPage,
    AllDataImportsPage,
    AddDataImportPage,
    SingleDataImportPage,
    DataImportCreateCategoryPage,
    DataImportAttachCategoryPage,
    RemoveDataImportPage
)


class UrlsTest(TestCase):
    """Test all URLs."""

    # ###########################
    # TEST ADMIN PAGES
    # ###########################

    def test_index_page_reverse(self):
        """Test reverser for index page."""
        reversed_url = reverse('geokey_dataimports:index')
        self.assertEqual(reversed_url, '/admin/dataimports/')

    def test_index_page_resolve(self):
        """Test resolver for index page."""
        resolved_url = resolve('/admin/dataimports/')
        self.assertEqual(resolved_url.func.__name__, IndexPage.__name__)

    def test_all_data_imports_page_reverse(self):
        """Test reverser for all data imports page."""
        reversed_url = reverse(
            'geokey_dataimports:all_dataimports',
            kwargs={'project_id': 1}
        )
        self.assertEqual(reversed_url, '/admin/projects/1/dataimports/')

    def test_all_data_imports_page_resolve(self):
        """Test resolver for all data imports page."""
        resolved_url = resolve('/admin/projects/1/dataimports/')
        self.assertEqual(
            resolved_url.func.__name__,
            AllDataImportsPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)

    def test_add_data_import_page_reverse(self):
        """Test reverser for adding data import page."""
        reversed_url = reverse(
            'geokey_dataimports:dataimport_add',
            kwargs={'project_id': 1}
        )
        self.assertEqual(reversed_url, '/admin/projects/1/dataimports/add/')

    def test_add_data_import_page_resolve(self):
        """Test resolver for adding data import page."""
        resolved_url = resolve('/admin/projects/1/dataimports/add/')
        self.assertEqual(
            resolved_url.func.__name__,
            AddDataImportPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)

    def test_single_data_import_page_reverse(self):
        """Test reverser for single data import page."""
        reversed_url = reverse(
            'geokey_dataimports:single_dataimport',
            kwargs={'project_id': 1, 'dataimport_id': 5}
        )
        self.assertEqual(reversed_url, '/admin/projects/1/dataimports/5/')

    def test_single_data_import_page_resolve(self):
        """Test resolver for single data import page."""
        resolved_url = resolve('/admin/projects/1/dataimports/5/')
        self.assertEqual(
            resolved_url.func.__name__,
            SingleDataImportPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['dataimport_id']), 5)

    def test_data_import_create_category_page_reverse(self):
        """Test reverser for data import creating category page."""
        reversed_url = reverse(
            'geokey_dataimports:dataimport_create_category',
            kwargs={'project_id': 1, 'dataimport_id': 5}
        )
        self.assertEqual(
            reversed_url,
            '/admin/projects/1/dataimports/5/create-category/'
        )

    def test_data_import_create_category_page_resolve(self):
        """Test resolver for data import creating category page."""
        resolved_url = resolve(
            '/admin/projects/1/dataimports/5/create-category/'
        )
        self.assertEqual(
            resolved_url.func.__name__,
            DataImportCreateCategoryPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['dataimport_id']), 5)

    def test_data_import_attach_category_page_reverse(self):
        """Test reverser for data import attaching category page."""
        reversed_url = reverse(
            'geokey_dataimports:dataimport_attach_category',
            kwargs={'project_id': 1, 'dataimport_id': 5}
        )
        self.assertEqual(
            reversed_url,
            '/admin/projects/1/dataimports/5/attach-category/'
        )

    def test_data_import_attach_category_page_resolve(self):
        """Test resolver for data import attaching category page."""
        resolved_url = resolve(
            '/admin/projects/1/dataimports/5/attach-category/'
        )
        self.assertEqual(
            resolved_url.func.__name__,
            DataImportAttachCategoryPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['dataimport_id']), 5)

    def test_remove_data_import_page_reverse(self):
        """Test reverser for removing data import page."""
        reversed_url = reverse(
            'geokey_dataimports:dataimport_remove',
            kwargs={'project_id': 1, 'dataimport_id': 5}
        )
        self.assertEqual(
            reversed_url,
            '/admin/projects/1/dataimports/5/remove/'
        )

    def test_remove_data_import_page_resolve(self):
        """Test resolver for removing data import page."""
        resolved_url = resolve('/admin/projects/1/dataimports/5/remove/')
        self.assertEqual(
            resolved_url.func.__name__,
            RemoveDataImportPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['dataimport_id']), 5)
