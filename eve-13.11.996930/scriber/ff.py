#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\ff.py


def o(format_str, *args):
    format_count = format_str.count('%')
    if not format_count:
        return format_str
    percent_count = format_str.count('%%')
    format_count -= percent_count * 2
    if not format_count:
        return format_str.replace('%%', '%')
    missing_args = format_count - len(args)
    if missing_args > 0:
        return format_str % (args + tuple([''] * missing_args))
    elif missing_args < 0:
        return format_str % args[:missing_args]
    else:
        return format_str % args


def pl(value, one_format = '', many_format = None, zero_format = None):
    if many_format is None:
        many_format = '%ss' % one_format
    if value == 0:
        if zero_format is not None:
            return o(zero_format, value)
        else:
            return o(many_format, value)
    else:
        if value == 1:
            return o(one_format, value)
        return o(many_format, value)
