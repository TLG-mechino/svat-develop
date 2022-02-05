import re


class DetectDeviceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        user_agent = request.META['HTTP_USER_AGENT']
        result = re.search(r"iPhone|iPad|iPod|Android|webOS|BlackBerry|Windows Phone", user_agent, re.IGNORECASE)
        request.is_mobile = result is not None
        
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        pass

    def process_template_response(self, request, response):
        pass
        
