import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template import TemplateSyntaxError
from django.views import generic

from email_editor.preview import get_preview_classes, extract_subject
from email_editor.settings import app_settings

if typing.TYPE_CHECKING:
    from email_editor.preview import EmailPreview


class EmailTemplatePreviewView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'email_editor/email-preview.html'
    errors = []

    def __init__(self, *args, **kwargs):
        self.is_preview_only = app_settings.PREVIEW_ONLY
        super().__init__(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)

    def dispatch(self, request, *args, **kwargs):

        self.errors = []
        if not request.user.is_staff:
            return HttpResponseForbidden('Forbidden')

        return super(EmailTemplatePreviewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_cls_list'] = get_preview_classes()
        context['tiny_mce_settings'] = app_settings.TINY_MCE_INIT
        context['editor_type'] = app_settings.WYSIWYG_EDITOR
        return context

    @staticmethod
    def get_preview_cls(request, preview_cls_str: str):
        if not preview_cls_str or preview_cls_str == "":
            return None

        cls_iter = filter(lambda item: item[0] == preview_cls_str, get_preview_classes())
        cls = next(cls_iter, None)
        if not cls:
            return
        return cls[1]

    def get(self, request, *args, **kwargs):
        preview_cls_str = request.GET.get('preview_cls')
        is_api_response = request.GET.get('api')

        PreviewCls = self.get_preview_cls(request, preview_cls_str)
        if not PreviewCls:
            return self.render_to_response(context=self.get_context_data())

        if not PreviewCls:
            return HttpResponseBadRequest()

        instance = PreviewCls()     # type: EmailPreview
        try:
            html = instance.render(request)
            subject = instance.subject
        except TemplateSyntaxError as e:
            subject = None
            html = None
            self.errors.append(e)

        context = {
            'html': html,
            'subject': subject,
            'errors': self.errors
        }

        if not self.is_preview_only:
            context = {
                'context_tree': instance.context_tree,
                'raw': instance.raw_content,
                **context
            }

        if is_api_response:
            return JsonResponse(context)

        return self.render_to_response({
            **context,
            **self.get_context_data()
        })

    def post(self, request, *args, **kwargs):
        if self.is_preview_only:
            return HttpResponseBadRequest('preview only')

        content = request.POST.get('content')
        preview_cls_str = request.GET.get('preview_cls')
        PreviewCls = self.get_preview_cls(request, preview_cls_str)
        if not PreviewCls:
            return self.get(request, *args, **kwargs)

        instance = PreviewCls()
        instance.write(content)

        return self.get(request, *args, **kwargs)