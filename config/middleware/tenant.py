class TenantMiddleware:
    """
    Middleware to resolve and attach the current tenant (CompanyProfile or CollegeProfile)
    to the incoming request based on the authenticated user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        if request.user and request.user.is_authenticated:
            role = getattr(request.user, "role", None)
            if role == "COMPANY":
                try:
                    request.tenant = request.user.company_profile_new
                except Exception:
                    pass
            elif role == "COLLEGE":
                try:
                    request.tenant = request.user.college_profile
                except Exception:
                    pass

        response = self.get_response(request)
        return response
