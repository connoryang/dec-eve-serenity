#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\filters.py
import datetime
import json
import datetimeutils
import typeutils
from scriber import htmlutils
from scriber import utils
from scriber import widgets
from scriber import ff

def date(date_obj, str_format = '%Y-%m-%d'):
    return datetime_filter(date_obj, str_format)


def time(date_obj, str_format = '%H:%M:%S'):
    return datetime_filter(date_obj, str_format)


def dt_sec(temporal_object):
    return datetime_filter(temporal_object, '%Y-%m-%d %H:%M:%S')


def dt_micro(temporal_object):
    return datetime_filter(temporal_object, '%Y-%m-%d %H:%M:%S.%f')


def dt(temporal_object):
    return datetime_filter(temporal_object)


@utils.filter_name('datetime')
def datetime_filter(temporal_object, str_format = '%Y-%m-%d %H:%M'):
    temporal_object = datetimeutils.any_to_datetime(temporal_object)
    if isinstance(temporal_object, datetime.datetime):
        return temporal_object.strftime(str_format)
    else:
        return temporal_object


def hide(content):
    return '<span style="display:none;text-indent:-10000;overflow:hidden;font-size:1px;color:#ffffff;">%s</span>' % content


def nl2br(content):
    return htmlutils.newline_to_html(content)


def unsanitize_html(content):
    return reduce(lambda h, n: h.replace(*n), (('&gt;', '>'), ('&lt;', '<')), content)


def a(model, icon_class = ''):
    url = None
    href_call = getattr(model, 'get_href', None)
    if href_call and hasattr(href_call, '__call__'):
        url = href_call()
    else:
        href = getattr(model._meta, 'href', None)
        if href and isinstance(href, (str, unicode)):
            url = href % model.get_id()
    if url:
        if icon_class == '':
            icon_class = getattr(model._meta, 'icon', '')
        if icon_class:
            icon_class = '<i class="icon icon-%s"></i> ' % icon_class
        return '<a href="%s">%s%s</a>' % (url, icon_class, model)
    return model


def btn_model(model, icon_class = ''):
    href = getattr(model._meta, 'href', None)
    if href:
        if icon_class == '':
            icon_class = getattr(model._meta, 'icon', '')
        if icon_class:
            icon_class = '<i class="icon icon-white icon-%s"></i> ' % icon_class
        return '<a class="btn btn-mini btn-info" href="%s">%s%s <i class="icon icon-share icon-white"></i></a>' % (href % model.get_id(), icon_class, model)
    return model


def btn(model_or_text, *args, **kwargs):
    if not isinstance(model_or_text, basestring):
        return btn_model(model_or_text)
    return model_or_text


def label(text, label_type = widgets.BADGE_DEFAULT):
    return widgets.Label.get(text, label_type)


def label_green(text):
    return widgets.Label.green(text)


def label_yellow(text):
    return widgets.Label.yellow(text)


def label_red(text):
    return widgets.Label.red(text)


def label_black(text):
    return widgets.Label.black(text)


def label_blue(text):
    return widgets.Label.blue(text)


def badge(text, label_type = widgets.BADGE_DEFAULT):
    return widgets.Badge.get(text, label_type)


def badge_green(text):
    return widgets.Badge.green(text)


def badge_yellow(text):
    return widgets.Badge.yellow(text)


def badge_red(text):
    return widgets.Badge.red(text)


def badge_black(text):
    return widgets.Badge.black(text)


def badge_blue(text):
    return widgets.Badge.blue(text)


def pl(value, one_format = '', many_format = None, zero_format = None):
    return ff.pl(value, one_format, many_format, zero_format)


def enum(model, field_name):
    try:
        return model._meta.field_map[field_name].enum_map[getattr(model, field_name)]
    except (KeyError, AttributeError):
        return getattr(model, field_name, model)


def seconds_ago(datetime_object):
    datetime_object = datetimeutils.any_to_datetime(datetime_object)
    if isinstance(datetime_object, datetime.datetime):
        return (datetime.datetime.now() - datetime_object).total_seconds()


def ago(delta_or_date):
    return datetimeutils.ago(delta_or_date, str(delta_or_date))


def ago_plus(datetime_object, ago_text = 'ago', str_format = '%Y-%m-%d %H:%M'):
    datetime_object = datetimeutils.any_to_datetime(datetime_object)
    if isinstance(datetime_object, datetime.datetime):
        return '%s %s <span class="muted">(%s)</span>' % (datetimeutils.ago(datetime_object, str(datetime_object)), ago_text, datetime_object.strftime(str_format))
    else:
        return '%s %s <span class="muted">(%s)</span>' % (datetimeutils.ago(datetime_object, str(datetime_object)), ago_text, str(datetime_object))


def ago_ttip(datetime_object, ago_text = 'ago', str_format = '%Y-%m-%d %H:%M'):
    datetime_object = datetimeutils.any_to_datetime(datetime_object)
    if isinstance(datetime_object, datetime.datetime):
        return '<span class="ttip" title="%s">%s %s</span>' % (datetime_object.strftime(str_format), datetimeutils.ago(datetime_object, str(datetime_object)), ago_text)
    else:
        return '<span class="ttip" title="%s">%s %s</span>' % (str(datetime_object), datetimeutils.ago(datetime_object, str(datetime_object)), ago_text)


def ago_ttip_sec(datetime_object, ago_text = 'ago'):
    return ago_ttip(datetime_object, ago_text, '%Y-%m-%d %H:%M:%S')


def deltastr(delta):
    return datetimeutils.deltastr(delta, str(delta))


def floatformat(value, precision = 2):
    value = typeutils.float_eval(value, None)
    if value is None:
        return ''
    return ('{:,.' + str(precision) + 'f}').format(value)


def iif(value, if_true, if_false = ''):
    if value:
        return if_true
    return if_false


def yn(value):
    return iif(value, 'Yes', 'No')


def ynlabel(value):
    return iif(value, widgets.Label.green('Yes'), widgets.Label.red('No'))


def ynico(value):
    return iif(value, '<i class="fa fa-check"></i>', '<i class="fa fa-times"></i>')


def ynoico(value):
    return iif(value, '<i class="fa fa-check-circle"></i>', '<i class="fa fa-times-circle"></i>')


def yncico(value):
    return iif(value, '<i class="fa fa-check text-success"></i>', '<i class="fa fa-times text-error"></i>')


def yncoico(value):
    return iif(value, '<i class="fa fa-check-circle text-success"></i>', '<i class="fa fa-times-circle text-error"></i>')


def sel(value):
    return iif(value, ' selected')


def chk(value):
    return iif(value, ' checked')


def qtable(data, dom_id = None, dom_classes = '+', dom_style = None, has_header = None, **kwargs):
    class_list = []
    if isinstance(dom_classes, (list, tuple)):
        if '+' in dom_classes:
            class_list.extend(widgets.QuickTable.DEFAULT_DOM_CLASSES)
            dom_classes.remove('+')
            class_list.extend(dom_classes)
    elif isinstance(dom_classes, str):
        if dom_classes.startswith('+'):
            class_list.extend(widgets.QuickTable.DEFAULT_DOM_CLASSES)
            if len(dom_classes) > 1:
                class_list.extend(dom_classes[1:].strip().split(' '))
    return widgets.QuickTable.get(data, dom_id, class_list, dom_style, has_header, **kwargs)


def jsontable(data, dom_id = None, dom_classes = '+', dom_style = None, recursive = True, **kwargs):
    if isinstance(data, dict):
        return dicttable(data, dom_id, dom_classes, dom_style, recursive, **kwargs)
    if isinstance(data, (list, tuple)):
        return listtable(data, dom_id, dom_classes, dom_style, recursive, **kwargs)
    if isinstance(data, (str, unicode)):
        data = data.strip()
        try:
            if data.startswith('{') and data.endswith('}'):
                data = json.loads(data)
                return dicttable(data, dom_id, dom_classes, dom_style, recursive, **kwargs)
            if data.startswith('[') and data.endswith(']'):
                data = json.loads(data)
                return listtable(data, dom_id, dom_classes, dom_style, recursive, **kwargs)
        except ValueError as ex:
            return listtable([data], dom_id, dom_classes, dom_style, recursive, **kwargs)

    else:
        return listtable([data], dom_id, dom_classes, dom_style, recursive, **kwargs)


def listtable(data_list, dom_id = None, dom_classes = '+', dom_style = None, recursive = True, **kwargs):
    if recursive:
        if not isinstance(recursive, bool):
            recursive -= 1
        parsed_list = []
        for i, line in enumerate(data_list):
            if isinstance(line, dict):
                parsed_list.append(dicttable(line, dom_id, dom_classes, dom_style, recursive, **kwargs))
            elif isinstance(line, (list, tuple)):
                parsed_list.append(listtable(line, dom_id, dom_classes, dom_style, recursive, **kwargs))
            else:
                parsed_list.append(line)

    else:
        parsed_list = data_list
    return qtable(parsed_list, dom_id, dom_classes, dom_style, False, **kwargs)


def dicttable(data_dict, dom_id = None, dom_classes = '+', dom_style = None, recursive = True, **kwargs):
    if recursive:
        if not isinstance(recursive, bool):
            recursive -= 1
        parsed_dict = {}
        for k, val in data_dict.iteritems():
            if isinstance(val, dict):
                parsed_dict[k] = dicttable(val, dom_id, dom_classes, dom_style, recursive, **kwargs)
            elif isinstance(val, (list, tuple)):
                parsed_dict[k] = listtable(val, dom_id, dom_classes, dom_style, recursive, **kwargs)
            else:
                parsed_dict[k] = val

    else:
        parsed_dict = data_dict
    return qtable(parsed_dict, dom_id, dom_classes, dom_style, False, **kwargs)


@utils.filter_name('json')
def to_json(dict_or_list):
    try:
        if isinstance(dict_or_list, basestring):
            dict_or_list = json.loads(dict_or_list)
        return json.dumps(dict_or_list, indent=4)
    except ValueError as ex:
        return dict_or_list


def pyid(obj):
    return str(id(obj))


def pyhash(obj):
    return str(hash(obj))


def currsym(value):
    if not value:
        return '&curren;'
    lvalue = value.lower()
    if lvalue == 'usd':
        return '&#36;'
    if lvalue == 'eur':
        return '&euro;'
    if lvalue == 'gbp':
        return '&pound;'
    if lvalue == 'jpy':
        return '&yen;'
    return value


def numformat(value):
    value = typeutils.int_eval(value, None)
    if not value:
        return ''
    return '{:,.0f}'.format(value)


def idx(value, *args):
    if not isinstance(value, int) or value < 0:
        return ''
    if isinstance(args, (list, tuple)):
        if len(args) == 1:
            if isinstance(args[0], (list, tuple)):
                args = args[0]
    if len(args) > value:
        return args[value]
    return ''


def stdtext(value, word_caps = True, acronym_length = 3):
    parts = value.split(' ')
    buff = []
    for part in parts:
        part = part.strip()
        if part.isupper():
            part = part.replace('_', ' ')
        else:
            partbuff = []
            for i, c in enumerate(part):
                if i != 0:
                    if c.isupper():
                        partbuff.append(' ')
                partbuff.append(c)

            part = ''.join(partbuff)
        buff.append(part)

    buff2 = []
    for w in ' '.join(buff).split(' '):
        if w.isupper():
            if 1 < len(w) <= acronym_length:
                buff2.append(w)
            elif word_caps:
                buff2.append(w.capitalize())
            else:
                buff2.append(w.lower())
        elif word_caps:
            buff2.append(w.capitalize())
        else:
            buff2.append(w.lower())

    if not word_caps:
        return ' '.join(buff).capitalize()
    else:
        return ' '.join(buff)
