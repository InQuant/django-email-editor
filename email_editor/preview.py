import abc
import inspect
import os
import re
from typing import Union

from django.template import loader, Template, Engine, TemplateSyntaxError
from django.template.backends.django import DjangoTemplates
from django.template.loader import _engine_list

CLASS_REGISTRY = []


def register(cls):
    CLASS_REGISTRY.append((cls.__name__, cls))


def get_preview_classes():
    return CLASS_REGISTRY


def extract_subject(template: Template) -> Union[str, None]:
    """
    This will extract the subject from a html file if it's in the first line like following format:

    e.g. <!-- Subject: test!! -->
    => results in "test!!"
    """
    html = template.render({})
    subject_regex = re.search(r'<!--.*[sS]ubject: *(?P<subject>.*) *-->', html)
    if not subject_regex:
        return
    return subject_regex.group('subject').strip()


class EmailPreview(abc.ABC):
    template_name = None

    def __init__(self):
        if not self.template_name:
            raise Exception(f'No "template_name" set in "{self.__class__.__name__}"')

    @staticmethod
    def _build_tree(item: dict, depth=0, max_depth=3):
        result = {}
        for key, value in item.items():
            if hasattr(value, "__class__") and hasattr(value, "__dict__"):
                if depth == max_depth:
                    result[key] = str(type(value))

                result[key] = EmailPreview._build_tree(value.__dict__, depth=depth + 1)
                continue

            if isinstance(value, dict):
                if depth == max_depth:
                    result[key] = value
                result[key] = EmailPreview._build_tree(value, depth=depth+1)
                continue

            result[key] = value

        return result

    @property
    def context_tree(self):
        context = self.get_template_context()
        tree = self._build_tree(context)
        return tree

    @property
    def path(self):
        try:
            return self.template.origin.name
        except TemplateSyntaxError:
            pass

        engines = _engine_list(using=None)
        for django_template in engines:
            django_template = django_template  # type: DjangoTemplates
            for t_dir in django_template.template_dirs:
                template_path = os.path.join(t_dir, self.template_name)
                is_file = os.path.isfile(f'{template_path}')
                if not is_file:
                    continue
                return template_path

    @property
    def raw_content(self):
        with open(self.path, 'r') as file:
            return file.read()

    @property
    def template(self):
        return loader.get_template(self.template_name)

    def get_template_context(self):
        raise NotImplementedError('No context defined')

    def render(self, request):
        context = self.get_template_context()
        return self.template.render(context=context, request=request).strip()