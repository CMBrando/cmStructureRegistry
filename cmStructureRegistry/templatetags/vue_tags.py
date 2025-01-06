from django import template
from django.conf import settings
from django.http import HttpResponse
import os.path

register = template.Library()

@register.simple_tag
def load_template(name):
    
    file_name = name + ".html"
    my_html_file = os.path.join(settings.STATIC_ROOT, 'cmStructureRegistry', 'components', "templates", file_name)

    with open(my_html_file) as f:
        content = f.read()

    return content