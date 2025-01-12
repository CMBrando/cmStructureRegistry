from django import template
from django.conf import settings
from django.http import HttpResponse
import os.path
from django.core.cache import cache

register = template.Library()

@register.simple_tag
def load_template(name):
    
    file_name = name + ".html"
    my_html_file = os.path.join(settings.STATIC_ROOT, 'cmStructureRegistry', 'components', "templates", file_name)

    content = cache.get('cmStructureRegistry_' + file_name)
    if content is None:
        with open(my_html_file) as f:
            content = f.read()
            cache.set('cmStructureRegistry_' + file_name, content, timeout=300)

    return content