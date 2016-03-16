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
from .models import DataImport
from .forms import DataImportForm


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
                    if self.request.POST.get('category_create') == 'false':
                        try:
                            form.instance.category = project.categories.get(
                                pk=self.request.POST.get('category')
                            )
                            messages.success(
                                self.request,
                                'The data import has been added.'
                            )
                        except Category.DoesNotExist:
                            messages.error(
                                self.request,
                                'The category does not exist. Please create a '
                                'new category.'
                            )
                    else:
                        messages.success(
                            self.request,
                            'The data import has been added. Please create a '
                            'new category in order to import data.'
                        )

                    return super(AddDataImportPage, self).form_valid(form)

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
                'geokey_dataimports:dataimport_attach_category',
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
        django.http.HttpResponse
            Rendered template.
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
                if not form.instance.category:
                    try:
                        form.instance.category = project.categories.get(
                            pk=self.request.POST.get('category')
                        )
                        messages.success(
                            self.request,
                            'The category has been associated with the data '
                            'import. Category fields can now be attached.'
                        )
                    except Category.DoesNotExist:
                        messages.error(
                            self.request,
                            'The category does not exist. Please create a '
                            'new category.'
                        )
                else:
                    messages.success(
                        self.request,
                        'The data import has been updated.'
                    )
                form.save()

                return super(SingleDataImportPage, self).form_valid(form)

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
        Set URL redirection when data import updated successfully.

        Returns
        -------
        str
            URL for redirection.
        """
        return reverse(
            'geokey_dataimports:single_dataimport',
            kwargs={
                'project_id': self.kwargs['project_id'],
                'dataimport_id': self.kwargs['dataimport_id']
            }
        )


class DataImportCreateCategoryPage(TemplateView):
    """Create category for data import page."""

    template_name = 'di_create_category.html'


class DataImportAttachCategoryPage(TemplateView):
    """Attach category for data import page."""

    template_name = 'di_attach_category.html'


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
