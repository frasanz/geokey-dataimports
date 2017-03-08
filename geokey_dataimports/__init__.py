"""Main initialisation for extension."""

VERSION = (0, 2, 1)
__version__ = '.'.join(map(str, VERSION))


try:
    from geokey.extensions.base import register

    register(
        'geokey_dataimports',
        'Data Imports',
        display_admin=True,
        superuser=False,
        version=__version__
    )
except BaseException:
    print 'Please install GeoKey first'
