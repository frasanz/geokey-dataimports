"""All views for the extension."""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, FormView, TemplateView
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin

from geokey.projects.models import Project
from geokey.projects.views import ProjectContext
from geokey.categories.models import Category

from .helpers.context_helpers import does_not_exist_msg
from .base import FORMAT
from .exceptions import FileParseError
from .models import DataImport
from .forms import CategoryForm, DataImportForm


# ###########################
# ADMIN PAGES
# ###########################

class IndexPage(LoginRequiredMixin, TemplateView):
    """Main index page."""

    template_name = 'di_index.html'

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        all projects (where user is an administrator) and available filters to
        the context. It optionally filters projects by the filter provided on
        the URL.

        Returns
        -------
        dict
            Context.
        """
        projects = Project.objects.filter(admins=self.request.user)

        filters = {}
        filter_for_projects = self.request.GET.get('filter')

        filter_to_add = 'without-data-imports-only'
        if filter_for_projects == filter_to_add:
            projects = projects.filter(dataimports__isnull=True).distinct()
        filters[filter_to_add] = 'Without data imports'

        filter_to_add = 'with-data-imports-only'
        if filter_for_projects == filter_to_add:
            projects = projects.filter(dataimports__isnull=False).distinct()
        filters[filter_to_add] = 'With data imports'

        return super(IndexPage, self).get_context_data(
            projects=projects,
            filters=filters,
            *args,
            **kwargs
        )


class AllDataImportsPage(LoginRequiredMixin, ProjectContext, TemplateView):
    """All data imports page."""

    template_name = 'di_all_dataimports.html'


class AddDataImportPage(LoginRequiredMixin, ProjectContext, CreateView):
    """Add new data import page."""

    template_name = 'di_add_dataimport.html'
    form_class = DataImportForm

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        project ID to the context.

        Returns
        -------
        dict
            Context.
        """
        project_id = self.kwargs['project_id']

        return super(AddDataImportPage, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        """
        Add data import when form data is valid.

        Parameters
        ----------
        form : geokey_dataimports.forms.DataImportForm
            Represents the user input.

        Returns
        -------
        django.http.HttpResponse
            Rendered template.
        """
        context = self.get_context_data(form=form)
        project = context.get('project')

        if project:
            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. New data imports cannot be added.'
                )
            else:
                form.instance.project = project
                form.instance.creator = self.request.user

                content_type = self.request.FILES.get('file').content_type

                if content_type == 'application/json':
                    form.instance.dataformat = FORMAT.GeoJSON
                elif content_type == 'application/vnd.google-earth.kml+xml':
                    form.instance.dataformat = FORMAT.KML
                elif content_type == 'text/csv':
                    form.instance.dataformat = FORMAT.CSV
                else:
                    messages.error(
                        self.request,
                        'The file type does not seem to be compatible with '
                        'this extension just yet. Only GeoJSON, KML and CSV '
                        'formats are supported.'
                    )

                if form.instance.dataformat:
                    try:
                        if self.request.POST.get('category_create') == 'false':
                            try:
                                category = project.categories.get(
                                    pk=self.request.POST.get('category')
                                )
                                form.instance.category = category
                            except Category.DoesNotExist:
                                messages.error(
                                    self.request,
                                    'The category does not exist.'
                                )

                        return super(AddDataImportPage, self).form_valid(form)
                    except FileParseError, error:
                        messages.error(self.request, error.to_html())
                    else:
                        messages.success(
                            self.request,
                            'The data import has been added.'
                        )

        return self.render_to_response(context)

    def form_invalid(self, form):
        """
        Display an error message when form data is invalid.

        Parameters
        ----------
        form : geokey_dataimports.forms.DataImportForm
            Represents the user input.

        Returns
        -------
        dict
            Context.
        """
        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """
        Set URL redirection when data import created successfully.

        Returns
        -------
        str
            URL for redirection.
        """
        if self.object.category:
            return reverse(
                'geokey_dataimports:dataimport_assign_fields',
                kwargs={
                    'project_id': self.kwargs['project_id'],
                    'dataimport_id': self.object.id
                }
            )
        else:
            return reverse(
                'geokey_dataimports:dataimport_create_category',
                kwargs={
                    'project_id': self.kwargs['project_id'],
                    'dataimport_id': self.object.id
                }
            )


class DataImportContext(LoginRequiredMixin, ProjectContext):
    """Get data import mixin."""

    def get_context_data(self, project_id, dataimport_id, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        a data import to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.
        dataimport_id : int
            Identifies the data import in the database.

        Returns
        -------
        dict
            Context.
        """
        context = super(DataImportContext, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        try:
            context['dataimport'] = DataImport.objects.get(
                pk=dataimport_id,
                project=context.get('project')
            )

            return context
        except DataImport.DoesNotExist:
            return {
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Data import')
            }


class SingleDataImportPage(DataImportContext, FormView):
    """Single data import page."""

    template_name = 'di_single_dataimport.html'

    def get_object(self):
        """
        Get and return data import object.

        Returns
        -------
        geokey_dataimports.models.DataImport
            Data import object.
        """
        try:
            return DataImport.objects.get(
                pk=self.kwargs['dataimport_id']
            )
        except DataImport.DoesNotExist:
            return None

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        project ID and data import ID to the context.

        Returns
        -------
        dict
            Context.
        """
        project_id = self.kwargs['project_id']
        dataimport_id = self.kwargs['dataimport_id']

        return super(SingleDataImportPage, self).get_context_data(
            project_id,
            dataimport_id,
            *args,
            **kwargs
        )

    def get_form(self, form_class=DataImportForm):
        """Attach instance object to form data."""
        return form_class(instance=self.get_object(), **self.get_form_kwargs())

    def form_valid(self, form):
        """
        Update data import when form data is valid.

        Parameters
        ----------
        form : geokey_dataimports.forms.DataImportForm
            Represents the user input.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to a single data import when form is saved, assign fields
            page when category is selected, create category page when category
            does not exist.
        django.http.HttpResponse
            Rendered template if project or data import does not exist.
        """
        context = self.get_context_data(form=form)
        project = context.get('project')

        if project:
            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Data imports cannot be updated.'
                )
            else:
                form.save()

                if not form.instance.category:
                    try:
                        form.instance.category = project.categories.get(
                            pk=self.request.POST.get('category')
                        )
                        form.save()

                        messages.success(
                            self.request,
                            'The category has been selected.'
                        )
                        return redirect(
                            'geokey_dataimports:dataimport_assign_fields',
                            project_id=project.id,
                            dataimport_id=form.instance.id
                        )
                    except Category.DoesNotExist:
                        messages.error(
                            self.request,
                            'The category does not exist. Please create a '
                            'new category.'
                        )
                        return redirect(
                            'geokey_dataimports:dataimport_create_category',
                            project_id=project.id,
                            dataimport_id=form.instance.id
                        )

                messages.success(
                    self.request,
                    'The data import has been updated.'
                )

        return self.render_to_response(context)

    def form_invalid(self, form):
        """
        Display an error message when form data is invalid.

        Parameters
        ----------
        form : geokey_dataimports.forms.DataImportForm
            Represents the user input.

        Returns
        -------
        dict
            Context.
        """
        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(self.get_context_data(form=form))


class DataImportCreateCategoryPage(DataImportContext, CreateView):
    """Create category for data import page."""

    template_name = 'di_create_category.html'
    form_class = CategoryForm

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        project ID and data import ID to the context.

        Returns
        -------
        dict
            Context.
        """
        project_id = self.kwargs['project_id']
        dataimport_id = self.kwargs['dataimport_id']

        return super(DataImportCreateCategoryPage, self).get_context_data(
            project_id,
            dataimport_id,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        """
        Create category and fields when form data is valid.

        Parameters
        ----------
        form : geokey_dataimports.forms.CategoryForm
            Represents the user input.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to a single data import when category is created.
        django.http.HttpResponse
            Rendered template if project or data import does not exist, project
            is locked, data import already has a category associated with it,
            fields already have been assigned.
        """
        data = self.request.POST
        context = self.get_context_data(form=form)
        dataimport = context.get('dataimport')

        if dataimport:
            if dataimport.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. New categories cannot be created.'
                )
            elif dataimport.category:
                messages.error(
                    self.request,
                    'The data import already has a category associated with '
                    'it. Unfortunately, this cannot be changed.'
                )
            elif dataimport.keys:
                messages.error(
                    self.request,
                    'The fields have already been assigned. Unfortunately, '
                    'this cannot be changed.'
                )
            else:
                dataimport.category = Category.objects.create(
                    name=form.instance.name,
                    description=form.instance.description,
                    project=dataimport.project,
                    creator=self.request.user
                )
                dataimport.save()

                ids = data.getlist('ids')
                keys = []

                if ids:
                    for datafield in dataimport.datafields.filter(id__in=ids):
                        datafield.convert_to_field(
                            data.get('fieldname_%s' % datafield.id),
                            datafield.key,
                            data.get('fieldtype_%s' % datafield.id)
                        )
                        keys.append(datafield.key)

                dataimport.keys = keys
                dataimport.save()

                messages.success(
                    self.request,
                    'The category has been created.'
                )
                return redirect(
                    'geokey_dataimports:single_dataimport',
                    project_id=dataimport.project.id,
                    dataimport_id=dataimport.id
                )

        return self.render_to_response(context)

    def form_invalid(self, form):
        """
        Display an error message when form data is invalid.

        Parameters
        ----------
        form : geokey_dataimports.forms.CategoryForm
            Represents the user input.

        Returns
        -------
        dict
            Context.
        """
        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(self.get_context_data(form=form))


class DataImportAssignFieldsPage(DataImportContext, TemplateView):
    """Assign fields for data import page."""

    template_name = 'di_assign_fields.html'

    def post(self, request, project_id, dataimport_id):
        """
        POST method for assigning fields.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        dataimport_id : int
            Identifies the data import in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to a single data import when fields are assigned.
        django.http.HttpResponse
            Rendered template if project or data import does not exist, project
            is locked, data import has no category associated with it, fields
            already have been assigned.
        """
        data = self.request.POST
        context = self.get_context_data(project_id, dataimport_id)
        dataimport = context.get('dataimport')

        if dataimport:
            if dataimport.project.islocked:
                messages.error(
                    request,
                    'The project is locked. Fields cannot be assigned.'
                )
            elif not dataimport.category:
                messages.error(
                    request,
                    'The data import has not category associated with it.'
                )
            elif dataimport.keys:
                messages.error(
                    request,
                    'Fields have already been assigned.'
                )
            else:
                ids = data.getlist('ids')
                keys = []
                changed_keys = {}

                if ids:
                    for datafield in dataimport.datafields.filter(id__in=ids):
                        key = data.get('existingfield_%s' % datafield.id)

                        if key:
                            changed_keys[datafield.key] = key
                        else:
                            key = datafield.key
                            field = datafield.convert_to_field(
                                data.get('fieldname_%s' % datafield.id),
                                key,
                                data.get('fieldtype_%s' % datafield.id)
                            )
                            if field.key != key:
                                changed_keys[key] = field.key

                        keys.append(datafield.key)

                    for datafeature in dataimport.datafeatures.all():
                        properties = datafeature.properties

                        for old_key, new_key in changed_keys.iteritems():
                            if old_key in properties:
                                properties[new_key] = properties.pop(old_key)

                        datafeature.properties = properties
                        datafeature.save()

                dataimport.keys = keys
                dataimport.save()

                messages.success(
                    self.request,
                    'The fields have been assigned.'
                )
                return redirect(
                    'geokey_dataimports:single_dataimport',
                    project_id=dataimport.project.id,
                    dataimport_id=dataimport.id
                )

        return self.render_to_response(context)


class DataImportAllDataFeaturesPage(DataImportContext, TemplateView):
    """Data import all data features page."""

    template_name = 'base.html'


class DataImportSingleDataFeaturePage(DataImportContext, TemplateView):
    """Data import single data feature page."""

    template_name = 'base.html'


class RemoveDataImportPage(DataImportContext, TemplateView):
    """Remove data import page."""

    template_name = 'base.html'

    def get(self, request, project_id, dataimport_id):
        """
        GET method for removing data import.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        dataimport_id : int
            Identifies the data import in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to all data imports if data import is removed, single
            data import page if project is locked.
        django.http.HttpResponse
            Rendered template if project or data import does not exist.
        """
        context = self.get_context_data(project_id, dataimport_id)
        dataimport = context.get('dataimport')

        if dataimport:
            if dataimport.project.islocked:
                messages.error(
                    request,
                    'The project is locked. Data import cannot be removed.'
                )
                return redirect(
                    'geokey_dataimports:single_dataimport',
                    project_id=project_id,
                    dataimport_id=dataimport_id
                )
            else:
                dataimport.delete()
                messages.success(
                    request,
                    'The data import has been removed.'
                )
                return redirect(
                    'geokey_dataimports:all_dataimports',
                    project_id=project_id
                )

        return self.render_to_response(context)
