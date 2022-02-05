from django.utils import translation
import apps.const.const as CONST


class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            # disable header request accept language
            del request.META['HTTP_ACCEPT_LANGUAGE']
        
        response = self.get_response(request)
        # remember language set by user
        response.set_cookie('django_language', translation.get_language())
        return response

    def process_exception(self, request, exception):
        pass

    def process_template_response(self, request, response):
        pass
        