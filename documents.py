# -*- coding: utf-8 -*-
import logging

from django.contrib.staticfiles import finders
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from weasyprint import CSS, HTML

logger = logging.getLogger('docmaker')


class PDFDocument(TemplateView):
    """
    A PDF document represents a certain PDF downloadable content. It provides all functionality to generate a
    pdf upon HTTP request. Internally it utilizes WeasyPrint - a HTML/CSS rendering engine for the pdf output with
    no command-line tool dependencies (such as wkhtmltopdf).
    """
    name = None
    url_name = None
    filename = None
    template_name = None
    css_files = []
    media_type = 'print'
    login_required = True

    class DocumentMeta:
        title = 'MyDocument'
        author = 'No Author'
        description = ''
        keywords = ''
        generator = 'WeasyPrint Document PDF Writer'
        created = ''
        modified = ''

    def get(self, request):
        # first, check if this report is for authenticated users only
        if self.login_required:
            if not request.user.is_authenticated:
                # raise a permission denied
                raise PermissionDenied

        # call the pre create hook
        self.pre_create()
        if request.GET.get('html') is not None:
            return HttpResponse(self._render(as_html=True))
        else:
            # create a report
            b_content = self._render()
            # Create the HttpResponse object with the appropriate PDF headers and content
            response = HttpResponse(b_content, content_type='application/pdf')
            # This cookie is needed if the download is done 'asynchronously' via jQueryFileDownload.js
            # It 'tells' the download-function that the download was done. Check out Return-Creation on how this is used
            response.set_cookie('fileDownload', 'true')
            if self.get_filename():
                response['Content-Disposition'] = 'attachment; filename="{filename}.pdf"'.format(
                    filename=self.get_filename())
            else:
                response['Content-Disposition'] = 'attachment; filename="{filename}.pdf"'.format(
                    filename=self.__class__.__name__)
        return response

    def pre_create(self):
        """
        The pre-create hook is called before the sheet gets created. It can be used for security checks, fetching data
        or updating the database (e.g. a counter).
        """
        pass

    def get_template(self):
        """
        This function is called to select the template for this request. It is then searched by the template finder.
        :return: The template name (String)
        """
        return self.template_name

    def get_context_data(self, **kwargs):
        """
        Sets up the context for the selected template.
        :param kwargs:
        :return: The context instance (Context)
        """
        # ctx = RequestContext(self.request)

        ctx = {}
        ctx['title'] = self.DocumentMeta.title
        ctx['author'] = self.DocumentMeta.author
        ctx['description'] = self.DocumentMeta.description
        ctx['keywords'] = self.DocumentMeta.keywords
        ctx['generator'] = self.DocumentMeta.generator
        ctx['created'] = self.DocumentMeta.modified
        ctx['modified'] = self.DocumentMeta.modified
        return ctx

    def get_document(self, html_str):
        """

        This hook provides the feature to retrieve the resulting WeasyPrint HTML instance for further modification.
        :param html_str: The rendered HTML string
        :return: a WeasyPrint HTML instance
        """
        try:
            base_url = self.request.build_absolute_uri()
        except AttributeError:
            base_url = None
        return HTML(string=html_str, media_type=self.media_type, base_url=base_url)

    def get_filename(self):
        """
        This function returns the filename for this request. It can be used to generate filenames based on the request.
        :return: The filename (String)
        """
        return self.filename or self.__class__.__name__ + '.pdf'

    def _render(self, as_html=False):
        # render all information to a binary output
        template_name = self.get_template()
        ctx = self.get_context_data()
        report_html = render_to_string(template_name, ctx)

        if as_html:
            return report_html
        else:
            additional_css = []
            for css in self.css_files:
                f = finders.find(css)
                if f:
                    additional_css.append(CSS(filename=f))
                else:
                    # silently fail in case a css file could not be found
                    logger.warn('Could not find css file {}'.format(css))

            html_doc = self.get_document(report_html)

            # create the binary data
            b_doc = html_doc.render(stylesheets=additional_css)
            return b_doc.write_pdf()


