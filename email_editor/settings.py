from enum import Enum

from django.conf import settings
from django.test.signals import setting_changed


class WYSIWYGEditor(str, Enum):
    TINY_MCE = 'tinymce'
    CKEDITOR = 'ckeditor'


DEFAULTS = {
    'PREVIEW_ONLY': False,
    'TINY_MCE_INIT': {
        'selector': '#htmlEditor',
        'plugins': ['code', 'table', 'link', 'lists', 'media', 'image', 'emoticons', 'quickbars', 'autoresize'],
        'entity_encoding': 'raw',

        'toolbar': 'undo redo | emoticons | blocks | styleselect | hr | bold italic |' +
                   'alignleft aligncenter alignright alignjustify |' +
                   'bullist numlist outdent indent | link image | code',

    },
    'WYSIWYG_EDITOR': WYSIWYGEditor.TINY_MCE
}


class AppSettings:
    """
    A settings object that allows the app settings to be accessed as
    properties. For example:
        from app_name.settings import app_settings
        print(app_settings.DEFAULT_NAME)
        
    Based on Django Rest Framework settings.py
    """
    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid App setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'EMAIL_EDITOR', {})
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()


app_settings = AppSettings(None, DEFAULTS)


def reload_app_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'EMAIL_EDITOR':
        app_settings.reload()


setting_changed.connect(reload_app_settings)
