import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template import TemplateSyntaxError
from django.urls import reverse
from django.utils import translation
from django.utils.translation import get_language
from django.views import generic

from email_editor.preview import get_preview_classes
from email_editor.settings import app_settings, WYSIWYGEditor

if typing.TYPE_CHECKING:
    from email_editor.preview import EmailPreview


class EmailTemplatePreviewView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'email_editor/email-preview.html'
    errors = []
    preview_cls = None
    editor = None

    def __init__(self, *args, **kwargs):
        self.is_preview_only = app_settings.PREVIEW_ONLY
        super().__init__(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('preview_cls'):
            return redirect(reverse('preview-template', kwargs={'preview_cls': request.GET['preview_cls']}))

        preview_cls_str = kwargs.get('preview_cls')
        print(preview_cls_str)
        if preview_cls_str:
            try:
                self.preview_cls = self.get_preview_cls(preview_cls_str)
            except ObjectDoesNotExist:
                return HttpResponseBadRequest('Not found')

        self.editor = request.GET.get('editor')
        self.errors = []

        if not request.user.is_staff:
            return redirect(f'{reverse("admin:login")}?next={request.get_full_path()}')

        return super(EmailTemplatePreviewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_cls_list'] = get_preview_classes()
        context['tiny_mce_settings'] = app_settings.TINY_MCE_INIT
        context['editor_list'] = [e.value for e in WYSIWYGEditor]
        return context

    def get_preview_cls(self, preview_cls_str):
        if not preview_cls_str or preview_cls_str == "":
            return None

        cls_iter = filter(lambda item: item[0] == preview_cls_str, get_preview_classes())
        cls = next(cls_iter, None)
        if not cls:
            raise ObjectDoesNotExist()
        return cls[1]

    def get(self, request, *args, **kwargs):
        is_api_response = request.GET.get('api')

        if not self.preview_cls:
            return self.render_to_response(context=self.get_context_data())

        if not self.preview_cls:
            return HttpResponseBadRequest()

        instance = self.preview_cls()     # type: EmailPreview
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
            'errors': self.errors,
            'editor_type': self.editor or app_settings.WYSIWYG_EDITOR
        }

        if not self.is_preview_only:
            context = {
                'context_tree': instance.context_tree,
                'raw': instance.raw_content,
                **context
            }

        if is_api_response:
            return JsonResponse(context)

        # set language
        if instance.language:
            translation.activate(instance.language)
            request.session[translation.LANGUAGE_SESSION_KEY] = instance.language

        return self.render_to_response({
            'language': get_language(),
            **context,
            **self.get_context_data()
        })

    def post(self, request, *args, **kwargs):
        if self.is_preview_only:
            return HttpResponseBadRequest('preview only')

        content = request.POST.get('content')
        if not self.preview_cls:
            return self.get(request, *args, **kwargs)

        instance = self.preview_cls()
        instance.write(content)

        return self.get(request, *args, **kwargs)