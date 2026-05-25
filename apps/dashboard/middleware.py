import hashlib
from datetime import date

SKIP_PREFIXES = ("/api/", "/static/", "/media/", "/admin/", "/assets/")


class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET" and not any(request.path.startswith(p) for p in SKIP_PREFIXES):
            from .models import SiteVisit
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
            ip = ip.split(",")[0].strip()
            ip_hash = hashlib.sha256(ip.encode()).hexdigest()
            try:
                SiteVisit.objects.get_or_create(date=date.today(), ip_hash=ip_hash)
            except Exception:
                pass
        return self.get_response(request)
