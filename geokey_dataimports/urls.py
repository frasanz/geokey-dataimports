"""All URLs for the extension."""

from django.conf.urls import url

from .views import (
    IndexPage,
    AllDataImportsPage,
    AddDataImportPage,
    SingleDataImportPage,
    DataImportCreateCategoryPage,
    DataImportAssignFieldsPage,
    DataImportAllDataFeaturesPage,
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
        r'dataimports/(?P<dataimport_id>[0-9]+)/assign-fields/$',
        DataImportAssignFieldsPage.as_view(),
        name='dataimport_assign_fields'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/(?P<dataimport_id>[0-9]+)/'
        r'datafeatures/$',
        DataImportAllDataFeaturesPage.as_view(),
        name='dataimport_all_datafeatures'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'dataimports/(?P<dataimport_id>[0-9]+)/remove/$',
        RemoveDataImportPage.as_view(),
        name='dataimport_remove')
]
