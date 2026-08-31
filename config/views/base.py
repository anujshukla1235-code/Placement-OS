from rest_framework.views import APIView


class TenantAwareAPIView(APIView):
    """
    Base APIView that automatically resolves and exposes self.tenant.
    Use this class for any API view that needs to scope operations to a tenant.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.tenant = getattr(request, "tenant", None)
