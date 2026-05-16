from django.urls import path
from .views import (
    ClearAllView,
    DeleteNotificationView,
    MarkAllReadView,
    MarkReadView,
    NotificationListView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("read-all/", MarkAllReadView.as_view(), name="notification-read-all"),
    path("clear-all/", ClearAllView.as_view(), name="notification-clear-all"),
    path("<int:pk>/read/", MarkReadView.as_view(), name="notification-read"),
    path("<int:pk>/", DeleteNotificationView.as_view(), name="notification-delete"),
]
