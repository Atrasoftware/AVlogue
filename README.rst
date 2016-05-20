AVlogue
============

AVlogue is a Django reusable app to manage, and automatically convert, audio and video files.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install avlogue

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/Atrasoftware/AVlogue.git#egg=avlogue

TODO: Describe further installation steps (edit / remove the examples below):

Add ``avlogue`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'avlogue',
    )

Add the ``avlogue`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^avlogue/', include('avlogue.urls')),
    )

Before your tags/filters are available in your templates, load them by using

.. code-block:: html

	{% load avlogue_tags %}


Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate avlogue


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 avlogue
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch

In order to run the tests, simply execute ``tox``.