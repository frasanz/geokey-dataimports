.. image:: https://img.shields.io/pypi/v/geokey-dataimports.svg
    :alt: PyPI Package
    :target: https://pypi.python.org/pypi/geokey-dataimports

.. image:: https://img.shields.io/travis/ExCiteS/geokey-dataimports/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/geokey-dataimports

.. image:: https://img.shields.io/coveralls/ExCiteS/geokey-dataimports/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/ExCiteS/geokey-dataimports

geokey-dataimports
==================

Import data from various formats (GeoJSON, KML, CSV) into GeoKey.

Install
-------

geokey-dataimports requires:

- Python version 2.7
- GeoKey version 1.4 or greater

Install the geokey-dataimports from PyPI:

.. code-block:: console

    pip install geokey-dataimports

Or from cloned repository:

.. code-block:: console

    cd geokey-dataimports
    pip install -e .

If you're cloning the repository and have GeoKey running within a Docker container, configure like such:

1. modify `Dockerfile` and add:

```
...
ADD /geokey /app
ADD /geokey-dataimports /extensions/geokey-dataimports
...
RUN pip install -e /app
RUN pip install -e /extensions/geokey-dataimports
```

2. modify `docker-compose.yml` and add a new volume:

```
...
volumes:
  - ./geokey:/app/geokey
  - ../geokey-dataimports/geokey_dataimports:/extensions/geokey-dataimports/geokey_dataimports
...
```

Add the package to installed apps:

.. code-block:: python

    INSTALLED_APPS += (
        ...
        'geokey_dataimports',
    )

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_dataimports

Copy static files:

.. code-block:: console

    python manage.py collectstatic

You're now ready to go!

Update
------

Update the geokey-dataimports from PyPI:

.. code-block:: console

    pip install -U geokey-dataimports

Migrate the new models into the database:

.. code-block:: console

    python manage.py migrate geokey_dataimports

Copy new static files:

.. code-block:: console

    python manage.py collectstatic

Test
----

Run tests:

.. code-block:: console

    python manage.py test geokey_dataimports

Check code coverage:

.. code-block:: console

    coverage run --source=geokey_dataimports manage.py test geokey_dataimports
    coverage report -m --omit=*/tests/*,*/migrations/*
