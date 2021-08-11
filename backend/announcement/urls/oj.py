from django.conf.urls import url, include

from ..views.oj import AnnouncementAPI, AnnouncementDetailAPI
from push_notifications.api.rest_framework import WebPushDeviceViewSet

urlpatterns = [
    url(r"^announcement/?$", AnnouncementAPI.as_view(), name="announcement_api"),
    url(r"^announcement_detail/?$", AnnouncementDetailAPI.as_view(), name="announcement_detail_api"),
    url(r'^wp_device?$', WebPushDeviceViewSet.as_view({'post': 'create'}), name='create_webpush_device'),
]
