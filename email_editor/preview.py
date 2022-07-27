import abc
import inspect
import os
import re
from typing import Union

from django.template import loader, Template, Engine, TemplateSyntaxError, Context
from django.template.backends.django import DjangoTemplates
from django.template.loader import _engine_list

is_post_office_installed = None

try:
    from post_office.models import EmailTemplate
    is_post_office_installed = True
except ModuleNotFoundError as e:
    is_post_office_installed = False

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
    is_post_office = False

    def __init__(self):
        if not self.template_name:
            raise Exception(f'No "template_name" set in "{self.__class__.__name__}"')

        if self.is_post_office and not is_post_office_installed:
            raise Exception(f'"post_office" is used by "{self.__class__.__name__}" but is not installed.')

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
    def subject(self):
        if self.is_post_office:
            return self.template.subject

        return extract_subject(self.template)

    def write(self, content):
        if self.is_post_office:
            template_instance = self.template
            template_instance.html_content = content
            template_instance.save()
            return

        with open(self.path, 'w') as file:
            file.write(content)

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
        if self.is_post_office:
            return self.template.html_content or self.template.content or ''

        with open(self.path, 'r') as file:
            return file.read()

    @property
    def template(self) -> Union[EmailTemplate, Template]:
        if self.is_post_office:
            try:
                return EmailTemplate.objects.get(name=self.template_name)
            except EmailTemplate.DoesNotExist as e:
                raise EmailTemplate.DoesNotExist(f'"{self.template_name}" - {e}')

        return loader.get_template(self.template_name)

    def get_template_context(self):
        raise NotImplementedError('No context defined')

    def render(self, request):
        context = self.get_template_context()

        if self.is_post_office:
            template = Template(self.template.html_content)
            return template.render(Context(context))

        return self.template.render(context=context, request=request).strip()