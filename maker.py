# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured

from docmaker.documents import PDFDocument


class AlreadyRegisteredException(Exception):
    pass


class NotRegisteredError(Exception):
    pass


class DocMaker(object):
    """
    The DocMaker class provides a wrapper functionality to print PDF using WeasyPrint. It also poses the view endpoints
    to download the documents to the client. Special input is to be handled using GET parameters.
    """

    def __init__(self, name='docmaker'):
        # registry for the documents to be available
        self._registry = {}
        self.name = name

    def register(self, document_klass, name=None):
        """
        Register a document to the pool.
        :param document_klass: The document class, musst have 'Document' as super type
        :param name: The name of this document
        """

        # Check if this document is already registered
        # there are 3 ways to register a document: explicit name during registration, by teh name property or class name
        if name:
            if name in self._registry:
                raise AlreadyRegisteredException('The document {doc} is already registered.'.format(doc=name))

        else:
            if document_klass.name and document_klass.name in self._registry:
                raise AlreadyRegisteredException('The document {doc} is already registered.'.format(
                        doc=document_klass.name))
            else:
                if document_klass.__name__ in self._registry:
                    raise AlreadyRegisteredException('The document {doc} is already registered.'.format(
                            doc=document_klass.name))

        if not issubclass(document_klass, PDFDocument):
            raise ImproperlyConfigured('The document {doc} is not a Document class'.format(doc=document_klass.__name__))

        if name:
            self._registry[name] = document_klass
        elif document_klass.name:
            self._registry[document_klass.name] = document_klass
        else:
            self._registry[document_klass.__name__] = document_klass

    def unregister(self, document_klass, name=None):
        """
        Removes a document from the registry, if already used elsewhere.
        """
        if name:
            if name in self._registry:
                if document_klass is not self._registry[name]:
                    raise NotRegisteredError('The document {doc} is not registered under the name {name}'.format(
                        doc=document_klass.__name__, name=name))
            else:
                raise NotRegisteredError('The name {name} is not registered'.format(name=name))
            del self._registry[name]
        else:
            if document_klass.name:
                if document_klass.name not in self._registry:
                    raise NotRegisteredError('The document {doc} is not registered'.format(doc=document_klass.__name__))
                del self._registry[document_klass.name]
            else:
                if document_klass.__name__ not in self._registry:
                    raise NotRegisteredError('The document {doc} is not registered'.format(doc=document_klass.__name__))
                del self._registry[document_klass.__name__]

    def get_urls(self):
        from django.conf.urls import url
        urlpatterns = []
        for name, view in self._registry.items():
            urlpatterns.append(url(r'^{name}/$'.format(name=view.url_name), view.as_view(), name=name))
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'documents', self.name

docmaker = DocMaker()









