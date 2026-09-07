from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'tenant_id') and request.user.tenant_id:
            request.tenant = request.user.tenant
        else:
            request.tenant = None


class TenantAwareMixin:
    """DRF mixin: sets request.tenant after authentication.

    Must be used with IsAuthenticated permission.
    Place this as the FIRST mixin so initial() sets tenant before the view code runs.
    """
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if user.is_authenticated and hasattr(user, 'tenant_id') and user.tenant_id:
            request.tenant = user.tenant
        else:
            request.tenant = None