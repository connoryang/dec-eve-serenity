#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\hooks.py
HOOKS = ['response']

def default_hooks():
    hooks = {}
    for event in HOOKS:
        hooks[event] = []

    return hooks


def dispatch_hook(key, hooks, hook_data, **kwargs):
    hooks = hooks or dict()
    if key in hooks:
        hooks = hooks.get(key)
        if hasattr(hooks, '__call__'):
            hooks = [hooks]
        for hook in hooks:
            _hook_data = hook(hook_data, **kwargs)
            if _hook_data is not None:
                hook_data = _hook_data

    return hook_data
