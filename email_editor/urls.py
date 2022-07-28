from django.urls import path

from email_editor.views import EmailTemplatePreviewView

urlpatterns = [
    path('', EmailTemplatePreviewView.as_view(), name='preview-template'),
    path('<preview_cls>/', EmailTemplatePreviewView.as_view(), name='preview-template'),
    path('<preview_cls>/<editor>/', EmailTemplatePreviewView.as_view(), name='preview-template'),
]