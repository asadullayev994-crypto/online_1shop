

from django.urls import path

from notifications.views import (
    NotificationListView,
    NotificationDetailView,
    NotificationReadAllView,
    NotificationPreferenceView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification_list"),
    path("read-all/", NotificationReadAllView.as_view(), name="notification_read_all"),
    path("preferences/", NotificationPreferenceView.as_view(), name="notification_preferences"),
    path("<int:notification_id>/", NotificationDetailView.as_view(), name="notification_detail"),
]