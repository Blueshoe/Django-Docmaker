# Django Docmaker
A Django app that makes creating PDFs out of HTML-Templates and with custom context-data easy.

A url for the PDFs download to the browser is generated automatically.


# Installation & Requirements
Copy this app into your Django project and add it to the `INSTALLED_APPS`.

[`WeasyPrint`](https://pypi.python.org/pypi/WeasyPrint/) is used to generate the PDF, install it via pip:
```
pip install weasyprint
```

Add the docmaker urls to your `urls.py` in the Django-root. This looks similar to this:
```
urls.py
from docmaker.maker import docmaker
urlpatterns = [
    url(_(r'^demo/'), include('app.demo', namespace='demo')),
    url(_(r'^account/'), include('app.account', namespace='account')),
    ... 
    url(r'^pdf/', docmaker.urls),
]
```
It is tested with Python 2.7 and Django 1.8

# Usage
The approach is that you can add a `documents.py` module to any of your existing Django apps. Within this module you can define the PDF documents that you wish to be able to create. 

### Declare your Documents
A PDF document represents a certain PDF downloadable content. It provides all functionality to generate a pdf upon HTTP request. 
Internally it utilizes WeasyPrint - a HTML/CSS rendering engine for the pdf output with no command-line tool dependencies (such as wkhtmltopdf).

A PDF document is a python class that inherits from `PDFDocument` and is placed inside the `documents.py` module in a given app.
It is registered to the docmaker using `docmaker.register(MyDocument)`

#### Attributes
* `name`: Slugified name of the PDF document, eg. 'my-document'.
* `url_name`: Slugified name that will be used in the url, eg 'my-document'. This is used to reference the document as a view in eg. Django's {% url %} template-tag. 
* `template_name`: (required unless you override `get_template()`) eg. `myapp/templates/myapp/pdf/my-document.html`.
* `filename`: (optional) Filename of the generated PDF file, eg. 'account.pdf'.
* `css_files`: (optional) List of css files that should be additionally used when rendering the template.
* `media_type`: (optional) The media type to use for `@media`.
* `login_required`: (optional) Boolean whether a login is required to request the document.

#### DocumentMeta
Set the meta data that will be attached to the pdf file

* `title`
* `author`
* `description`
* `keywords` (String)
* `generator`
* `created`
* `modified`
This data can also be overridden in `get_context_data`.

#### Hooks
To be flexible there are a couple of hooks you can extend or override in your document:

* `def get(self, request)`
* `def pre_create(self)`
* `def get_template(self)`
* `def get_context_data(self, **kwargs)`
* `def get_document(self, html_str)`
* `def get_filename(self)`

Most importantly, use `get_context_data` to pass data to your template.

#### Complete example of a PDFDocument
```
documents.py
# -*- coding: utf-8 -*-
from django.http import Http404
from docmaker.documents import PDFDocument
from docmaker.maker import docmaker


class AccountDocument(PDFDocument):
    name = 'account-document'
    url_name = 'account-document'

    username = None  # Will be passed as a GET parameter

    class DocumentMeta:
        title = 'Account Overview'
        author = 'Blueshoe'
        description = ''
        keywords = ''
        generator = ''
        created = ''
        modified = ''

    def pre_create(self):
        # Fetch some data from the GET request
        username = self.request.GET.get('username')
        if not username:
            raise Http404
        self.username = username

    def get_filename(self):
        return 'Account-Overview-{}.pdf'.format(self.username)

    def get_template(self):
        # Use any logic to choose between possible templates
        if self.is_premium_user(self.username):
            return 'app/pdf/account_premium.html'
        else:
            return 'app/pdf/account_simple.html'

    def get_context_data(self, **kwargs):
        ctx = super(AccountDocument, self).get_context_data(**kwargs)
        if self.is_premium_user(self.username):
            ctx['title'] = 'Replaced PDF title because he\'s a premium user' 
        ctx['any_value'] = 'Dummy Value'
        return ctx

    def is_premium_user(self, username):
        return True


docmaker.register(AccountDocument)
```

Take a look at the next two sections on how to create this document.

### Use it in a template
As stated are `PDFDocuments` well-known `TemplateViews`. This means we can use it's URL that docmaker is generating automatically and for exmaple request the PDF's via a link in a Template:
```
<a href="{% url 'app:documents:account-document' %}?username='maxmustermann'">
```

### Use it in views
You can return a PDF as the response to a given view, like the following:
```
def form_valid(self, form):
    ...
    return HttpResponse(reverse('app:documents:my-document')+'?username={}'.format(self.object.username))
```

### Creating HTML templates for your PDFs
Just write the PDF in HTML and CSS and make use of Django's template engine as you're used to it. For Details on some constraints, you might refer to the [WeasyPrint Documentation](http://weasyprint.org/docs/) .
It's recommended to add the templates inside a pdf folder in your apps template/app/ folder to keep the pdf templates separated from the ones of views. Eg. `myapp/templates/myapp/pdf/my-document.html`

# Authors
* [Michael Schilonka](https://github.com/Schille)