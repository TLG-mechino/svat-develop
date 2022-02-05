from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings


class AdminAuthenticateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        full_path = request.build_absolute_uri()
        if settings.LOGIN_URL not in full_path and "admin/" in full_path:
            if request.user.is_authenticated:
                if request.user.role == 1:
                    logout(request)
                    return redirect('user.index')
            else:
                return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        

        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        pass

    def process_template_response(self, request, response):
        pass
        