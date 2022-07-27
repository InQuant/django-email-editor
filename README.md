# Django Email Editor

Fast and easy way to edit and manage email templates.

![email_editor](https://user-images.githubusercontent.com/17835639/180997275-eaa66c95-fda0-4003-be44-99077195a062.png)

### Install

Add `email_editor` to your INSTALLED_APPS in django's `settings.py`:

```python
INSTALLED_APPS = (
    # ...
    "email_editor",
    # ...
)
```

And add the frontend path to `url.py`:

```python
# for example like this
from django.conf.urls import url
from django.contrib import admin

from email_editor.views import EmailTemplatePreviewView

urlpatterns = [
    url(r'^admin/preview/', EmailTemplatePreviewView.as_view()),

    url(r'^admin/', admin.site.urls),
]
```

### Quickstart

Define a preview class:

```python
from django.contrib.auth import get_user_model
from email_editor.preview import register, EmailPreview


@register
class WelcomeEmailPreview(EmailPreview):
    template_name = 'path/to/template/welcome_mail.html'
    
    # change this to true if you choose a post office email template in "template_name"
    is_post_office = False

    def get_template_context(self):
        return {
            'user': get_user_model().objects.first(),
            'test': {
                'Test': 'test'
            }
        }

```

This will make the Template visible to the view.


#### Adding a subject to email template

Simply add following code to the beginning of the file:

```html
<!-- Subject: Your awesome Subject! -->

<div>
  <h1>Welcome Email</h1>
  <div>Lorem Ispum dolor sit amet</div>
</div>
```

## Settings

These are the default settings for the module.

```python
EMAIL_EDITOR = {
    # show only template previews without editor 
    'PREVIEW_ONLY': False,

    # tinymce default init parameters
    'TINY_MCE_INIT': {
        'selector': '#htmlEditor',
        'plugins': ['code', 'link', 'image', 'emoticons', 'quickbars', 'autoresize'],
        'entity_encoding': 'raw',
        'toolbar': 'undo redo | styleselect | bold italic |' +
                   'alignleft aligncenter alignright alignjustify |' +
                   'bullist numlist outdent indent | link image | code emoticons hr',

    },

    # change editor ('ckeditor' | 'tinymce')
    'WYSIWYG_EDITOR': 'tinymce'
}
```