from demo.views import DocumentCreateView, DocumentListView
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def favicon_view(request):
    return HttpResponse(status=204)  # No content response


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DocumentListView.as_view(), name="document_list"),
    path("create/", DocumentCreateView.as_view(), name="document_create"),
    path("favicon.ico", favicon_view),
]
