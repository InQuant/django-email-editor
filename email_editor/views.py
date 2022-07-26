from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template import TemplateSyntaxError
from django.views import generic

from email_editor.preview import get_preview_classes, extract_subject


class EmailTemplatePreviewAdmin(LoginRequiredMixin, generic.TemplateView):
    template_name = 'email_editor/email-preview.html'
    errors = []

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.errors = []
        if not request.user.is_staff:
            return HttpResponseForbidden('Forbidden')

        return super(EmailTemplatePreviewAdmin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_cls_list'] = get_preview_classes()
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

        instance = PreviewCls()
        try:
            html = instance.render(request)
            subject = extract_subject(instance.template)
        except TemplateSyntaxError as e:
            subject = None
            html = None
            self.errors.append(e)

        context = {
            'html': html,
            'context_tree': instance.context_tree,
            'raw': instance.raw_content,
            'subject': subject,
            'errors': self.errors
        }

        if is_api_response:
            return JsonResponse(context)

        return self.render_to_response({
            **context,
            **self.get_context_data()
        })

    def post(self, request, *args, **kwargs):
        content = request.POST.get('content')
        preview_cls_str = request.GET.get('preview_cls')
        PreviewCls = self.get_preview_cls(request, preview_cls_str)
        if not PreviewCls:
            return self.get(request, *args, **kwargs)

        instance = PreviewCls()
        template_path = instance.path

        with open(template_path, 'w') as file:
            file.write(content)

        return self.get(request, *args, **kwargs)