from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from email_editor.views import EmailTemplatePreviewView

urlpatterns = [
    url(r'^admin/preview/', EmailTemplatePreviewView.as_view()),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)