from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path
from django.views import View
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.orders.views import CartView


class ReactAppView(View):
    """Serve the React SPA index.html for all non-API routes."""

    def get(self, request, *args, **kwargs):
        index = getattr(settings, "REACT_BUILD_DIR", None)
        if index is None:
            raise Http404
        index_file = index / "index.html"
        if not index_file.exists():
            raise Http404
        return FileResponse(open(index_file, "rb"), content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/cart/", CartView.as_view(), name="cart"),
    path("api/store/", include("apps.store.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/pos/", include("apps.pos.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    re_path(r"^(?!api/|admin/|static/|media/|assets/).*$", ReactAppView.as_view(), name="react-app"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
