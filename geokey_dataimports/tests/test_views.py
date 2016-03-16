"""All tests for views."""

import os

from django.core.files import File
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase, RequestFactory
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from .helpers import file_helpers
from ..helpers.context_helpers import does_not_exist_msg
from .model_factories import DataImportFactory
from ..models import DataImport
from ..forms import DataImportForm
from ..views import (
    IndexPage,
    AllDataImportsPage,
    AddDataImportPage,
    SingleDataImportPage,
    DataImportCreateCategoryPage,
    DataImportAttachCategoryPage,
    RemoveDataImportPage
)


no_rights_to_access_msg = 'You are not member of the administrators group ' \
                          'of this project and therefore not allowed to ' \
                          'alter the settings of the project'


# ###########################
# TESTS FOR ADMIN PAGES
# ###########################

class IndexPageTest(TestCase):
    """Test index page."""

    def setUp(self):
        """Set up test."""
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.view = IndexPage.as_view()
        self.filters = {
            'without-data-imports-only': 'Without data imports',
            'with-data-imports-only': 'With data imports'
        }

        self.user = UserFactory.create()

        self.project_1 = ProjectFactory.create(add_admins=[self.user])
        self.project_2 = ProjectFactory.create(add_admins=[self.user])
        self.project_3 = ProjectFactory.create(add_contributors=[self.user])
        self.project_4 = ProjectFactory.create()
        DataImportFactory.create(project=self.project_2)
        DataImportFactory.create(project=self.project_3)

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def tearDown(self):
        """Tear down test."""
        for dataimport in DataImport.objects.all():
            if dataimport.file:
                dataimport.file.delete()

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should render the page with all projects, where user is an
        administrator.
        """
        projects = [self.project_1, self.project_2]

        self.request.user = self.user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'di_index.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'messages': get_messages(self.request),
                'filters': self.filters,
                'projects': projects
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_user_only_without_dataimports(self):
        """
        Test GET with with user, but only projects without data imports.

        It should render the page with all projects, where user is an
        administrator. Those projects must also not have data imports.
        """
        projects = [self.project_1]

        self.request.user = self.user
        self.request.GET['filter'] = 'without-data-imports-only'
        response = self.view(self.request).render()

        rendered = render_to_string(
            'di_index.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'messages': get_messages(self.request),
                'filters': self.filters,
                'projects': projects,
                'request': {
                    'GET': {
                        'filter': self.request.GET.get('filter')
                    }
                }
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_user_only_with_dataimports(self):
        """
        Test GET with with user, but only projects with data imports.

        It should render the page with all projects, where user is an
        administrator. Those projects must also have data imports
        """
        projects = [self.project_2]

        self.request.user = self.user
        self.request.GET['filter'] = 'with-data-imports-only'
        response = self.view(self.request).render()

        rendered = render_to_string(
            'di_index.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'messages': get_messages(self.request),
                'filters': self.filters,
                'projects': projects,
                'request': {
                    'GET': {
                        'filter': self.request.GET.get('filter')
                    }
                }
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )


class AllDataImportsPageTest(TestCase):
    """Test all data imports page."""

    def setUp(self):
        """Set up test."""
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.view = AllDataImportsPage.as_view()

        self.user = UserFactory.create()
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'di_all_dataimports.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'di_all_dataimports.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Permission denied.',
                'error_description': no_rights_to_access_msg
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should render the page with a project.
        """
        self.request.user = self.admin
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'di_all_dataimports.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'project': self.project
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that project does not exist.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id + 123
        ).render()

        rendered = render_to_string(
            'di_all_dataimports.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )


class AddDataImportPageTest(TestCase):
    """Test add data import page."""

    def setUp(self):
        """Set up test."""
        self.factory = RequestFactory()
        self.request = HttpRequest()
        self.view = AddDataImportPage.as_view()

        self.user = UserFactory.create()
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            project=self.project
        )

        self.data = {
            'name': 'Test Import',
            'description': '',
            'dataformat': 'CSV',
            'file': File(open(file_helpers.get_csv_file().name)),
            'category_create': 'true'
        }
        self.url = reverse('geokey_dataimports:dataimport_add', kwargs={
            'project_id': self.project.id
        })

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def tearDown(self):
        """Tear down test."""
        for dataimport in DataImport.objects.all():
            if dataimport.file:
                dataimport.file.delete()

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        form = DataImportForm()
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        form = DataImportForm()
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Permission denied.',
                'error_description': no_rights_to_access_msg
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should render the page with a project.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        form = DataImportForm()
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'project': self.project
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that project does not exist.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id + 123
        ).render()

        form = DataImportForm()
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project'),
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_post_with_anonymous(self):
        """
        Test POST with with anonymous.

        It should redirect to login page.
        """
        request = self.factory.post(self.url, self.data)
        request.user = AnonymousUser()

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_user(self):
        """
        Test POST with with user.

        It should not allow to add new data imports, when user is not an
        administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        form = DataImportForm(data=self.data)
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 0)

    def test_post_with_contributor(self):
        """
        Test POST with with contributor.

        It should not allow to add new data imports, when user is not an
        administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.contributor

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        form = DataImportForm(data=self.data)
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Permission denied.',
                'error_description': no_rights_to_access_msg
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 0)

    def test_post_with_admin_when_creating_new_category(self):
        """
        Test POST with with admin, when creating a new category.

        It should add new data import, when user is an administrator. Also, it
        should redirect to a page to add a new category.
        """
        self.data['category_create'] = 'true'
        self.data['category'] = None
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_dataimports:dataimport_create_category',
                kwargs={
                    'project_id': self.project.id,
                    'dataimport_id': DataImport.objects.first().id
                }
            ),
            response['location']
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_post_with_admin_when_attaching_existing_category(self):
        """
        Test POST with with admin, when attaching an existing category.

        It should add new data import, when user is an administrator. Also, it
        should redirect to a page to attach an existing category.
        """
        self.data['category_create'] = 'false'
        self.data['category'] = self.category.id
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_dataimports:dataimport_attach_category',
                kwargs={
                    'project_id': self.project.id,
                    'dataimport_id': DataImport.objects.first().id
                }
            ),
            response['location']
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_post_when_no_project(self):
        """
        Test POST with with admin, when project does not exist.

        It should inform user that project does not exist.
        """
        self.data['category_create'] = 'true'
        self.data['category'] = None
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id + 123
        ).render()

        form = DataImportForm(data=self.data)
        rendered = render_to_string(
            'di_add_dataimport.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 0)

    def test_post_when_no_category(self):
        """
        Test POST with with admin, when category does not exist.

        It should add new data import, when user is an administrator. Also, it
        should redirect to a page to attach an existing category and inform
        user that category was not found.
        """
        self.data['category_create'] = 'false'
        self.data['category'] = self.category.id + 123
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_dataimports:dataimport_create_category',
                kwargs={
                    'project_id': self.project.id,
                    'dataimport_id': DataImport.objects.first().id
                }
            ),
            response['location']
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_post_when_project_is_locked(self):
        """
        Test POST with with admin, when project is locked.

        It should not add new import, when project is locked.
        """
        self.project.islocked = True
        self.project.save()

        self.data['category_create'] = 'true'
        self.data['category'] = None
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DataImport.objects.count(), 0)


class RemoveDataImportPageTest(TestCase):
    """Test remove data import page."""

    def setUp(self):
        """Set up test."""
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.view = RemoveDataImportPage.as_view()

        self.user = UserFactory.create()
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.dataimport = DataImportFactory.create(project=self.project)
        self.file = self.dataimport.file.path

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def tearDown(self):
        """Tear down test."""
        for dataimport in DataImport.objects.all():
            if dataimport.file:
                dataimport.file.delete()

        if os.path.isfile(self.file):
            os.remove(self.file)

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(
            self.request,
            project_id=self.project.id,
            dataimport_id=self.dataimport.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        response = self.view(
            self.request,
            project_id=self.project.id,
            dataimport_id=self.dataimport.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Data import')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        response = self.view(
            self.request,
            project_id=self.project.id,
            dataimport_id=self.dataimport.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Data import')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should remove import and redirect to all imports of a project.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id,
            dataimport_id=self.dataimport.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_dataimports:all_dataimports',
                kwargs={'project_id': self.project.id}
            ),
            response['location']
        )
        self.assertEqual(DataImport.objects.count(), 0)

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that data import does not exist.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id + 123,
            dataimport_id=self.dataimport.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Data import')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_get_when_no_import(self):
        """
        Test GET with with admin, when import does not exist.

        It should inform user that data import does not exist.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id,
            dataimport_id=self.dataimport.id + 123
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Data import')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(DataImport.objects.count(), 1)

    def test_get_when_project_is_locked(self):
        """
        Test GET with with admin, when project is locked.

        It should inform user that the project is locked and redirect to the
        same data import.
        """
        self.project.islocked = True
        self.project.save()

        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id,
            dataimport_id=self.dataimport.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_dataimports:single_dataimport',
                kwargs={
                    'project_id': self.project.id,
                    'dataimport_id': self.dataimport.id
                }
            ),
            response['location']
        )
        self.assertEqual(DataImport.objects.count(), 1)
