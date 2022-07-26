from django.contrib.auth.models import User

from email_editor.preview import register, EmailPreview


@register
class WelcomeEmailPreview(EmailPreview):
    template_name = 'test_project/welcome_mail.html'

    def get_template_context(self):
        return {
            'user': User.objects.first(),
            'test': {
                'Test': 'test'
            }
        }
