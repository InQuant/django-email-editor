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





