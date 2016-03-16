#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\werkzeug\debug\utils.py
from os.path import join, dirname
from werkzeug.templates import Template

def get_template(filename):
    return Template.from_file(join(dirname(__file__), 'templates', filename))


def render_template(template_filename, **context):
    return get_template(template_filename).render(**context)
