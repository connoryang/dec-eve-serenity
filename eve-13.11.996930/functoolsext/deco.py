#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\functoolsext\deco.py


def permacache(ignore_parameters = False):
    real_func = None
    if hasattr(ignore_parameters, '__call__'):
        real_func = ignore_parameters
        ignore_parameters = False
    cache = {}

    def inner(func):

        def innerer(*iargs, **ikwargs):
            if ignore_parameters:
                key = str(func)
            else:
                key = (str(iargs), str(ikwargs))
            if key not in cache:
                cache[key] = func(*iargs, **ikwargs)
            return cache[key]

        return innerer

    if real_func:
        return inner(real_func)
    else:
        return inner
