# -*- coding: utf-8 -*-
from django.conf import settings
import importlib
import imp as _imp


# autodiscover all documents
def autodiscover_documents():
    for app in settings.INSTALLED_APPS:
        # Django 1.7 allows for speciying a class name in INSTALLED_APPS.
        # (Issue #2248).
        try:
            importlib.import_module(app)
        except ImportError:
            package, _, _ = app.rpartition('.')

        try:
            pkg_path = importlib.import_module(app).__path__
        except AttributeError:
            continue

        try:
            _imp.find_module('documents', pkg_path)
        except ImportError:
            continue

        importlib.import_module('{0}.{1}'.format(app, 'documents'))

autodiscover_documents()
