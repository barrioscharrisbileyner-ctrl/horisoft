from .models import AuditEvent


class AuditMiddleware:
    write_methods = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in self.write_methods:
            return self.get_response(request)

        status_code = 500
        try:
            response = self.get_response(request)
            status_code = response.status_code
            return response
        finally:
            user = getattr(request, 'user', None)
            actor = user if user is not None and user.is_authenticated else None
            AuditEvent.objects.create(
                actor=actor,
                method=request.method,
                path=request.path_info[:500],
                status_code=status_code,
            )
