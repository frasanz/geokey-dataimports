"""All URLs for the extension."""

from django.conf.urls import url

from .views import (
    IndexPage,
    AllDataImportsPage,
    AddDataImportPage,
    SingleDataImportPage,
    DataImportCreateCategoryPage,
    DataImportAttachCategoryPage,
    RemoveDataImportPage
)


urlpatterns = [
    # ###########################
    # ADMIN PAGES
    # ###########################

    url(
        r'^admin/dataimports/$',
        IndexPage.as_view(),
        name='index'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/$',
        AllDataImportsPage.as_view(),
        name='all_dataimports'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/add/$',
        AddDataImportPage.as_view(),
        name='dataimport_add'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/(?P<dataimport_id>[0-9]+)/$',
        SingleDataImportPage.as_view(),
        name='single_dataimport'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/(?P<dataimport_id>[0-9]+)/create-category/$',
        DataImportCreateCategoryPage.as_view(),
        name='dataimport_create_category'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/(?P<dataimport_id>[0-9]+)/attach-category/$',
        DataImportAttachCategoryPage.as_view(),
        name='dataimport_attach_category'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/(?P<dataimport_id>[0-9]+)/remove/$',
        RemoveDataImportPage.as_view(),
        name='dataimport_remove')
]
