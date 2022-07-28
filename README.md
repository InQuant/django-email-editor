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

from django.urls import include

urlpatterns = [
    url(r'^admin/preview/', include('email_editor.urls')),
    
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
    # change language to edit multilang templates
    language = 'de' 

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
        # e.g. keys: plugins, toolbar ... 
    },

    # change editor ('ckeditor' | 'tinymce')
    'WYSIWYG_EDITOR': 'ckeditor',
    
    # preview show context: set max depth
    'CONTEXT_TREE_MAX_DEPTH': 3
}
```

## Editors

Available Editors:
- ACE
- CKEditor
- TinyMCE

## Additional

If you want to extract subjects from the html email template the ```django-email-editor``` way, 
you can use the ```extract_subject``` function.

```python
from django.template import loader

# import the function
from email_editor.preview import extract_subject

template = loader.get_template('your_app/your_template_name.html')

"""
Dont forget to put the subject into the html file like that: 
'<!-- Subject: Your Subject --> ...' 
at the beginning of your template file
"""


mail.send(
    subject=extract_subject(template),
    recipients=['test@localhost'],
    # ...
)
```