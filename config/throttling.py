from rest_framework.throttling import SimpleRateThrottle


class TenantRateThrottle(SimpleRateThrottle):
    """
    Rate-limits requests per authenticated tenant (user id), instead of the global
    per-IP/per-anonymous-user default. This matters in a multi-tenant B2B setup because
    the default DRF UserRateThrottle still applies a *shared* rate scope across all
    authenticated users — a single company hammering the API can eat into the same
    bucket every other tenant draws from if they're grouped behind the same proxy/NAT.
    Keying explicitly by user id keeps each tenant's quota independent.

    Mirrors ScopedRateThrottle's pattern: set `throttle_scope` on the view (not `scope`
    directly on this class) so different endpoints can have different tenant-scoped
    limits — e.g. throttle_scope = 'bulk_upload' or 'job_post'. The scope name must have
    a matching entry in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].
    """

    def __init__(self):
        # Deliberately skip SimpleRateThrottle.__init__ (which calls get_rate() and
        # requires self.scope to already be set) — the scope isn't known until
        # allow_request() reads it off the view, so rate/num_requests/duration are
        # resolved there instead.
        pass

    def allow_request(self, request, view):
        # Pull the scope from the view, same mechanism DRF's ScopedRateThrottle uses.
        self.scope = getattr(view, "throttle_scope", None)
        if not self.scope:
            return True  # view didn't opt into tenant throttling — don't block it
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None  # anonymous requests fall back to AnonRateThrottle instead
        return self.cache_format % {
            "scope": self.scope,
            "ident": str(request.user.id),
        }
