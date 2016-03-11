#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\pathtools\patterns.py
from fnmatch import fnmatch, fnmatchcase
__all__ = ['match_path',
 'match_path_against',
 'match_any_paths',
 'filter_paths']

def _string_lower(s):
    return s.lower()


def match_path_against(pathname, patterns, case_sensitive = True):
    if case_sensitive:
        match_func = fnmatchcase
        pattern_transform_func = lambda w: w
    else:
        match_func = fnmatch
        pathname = pathname.lower()
        pattern_transform_func = _string_lower
    for pattern in set(patterns):
        pattern = pattern_transform_func(pattern)
        if match_func(pathname, pattern):
            return True

    return False


def _match_path(pathname, included_patterns, excluded_patterns, case_sensitive = True):
    if not case_sensitive:
        included_patterns = set(map(_string_lower, included_patterns))
        excluded_patterns = set(map(_string_lower, excluded_patterns))
    else:
        included_patterns = set(included_patterns)
        excluded_patterns = set(excluded_patterns)
    common_patterns = included_patterns & excluded_patterns
    if common_patterns:
        raise ValueError('conflicting patterns `%s` included and excluded' % common_patterns)
    return match_path_against(pathname, included_patterns, case_sensitive) and not match_path_against(pathname, excluded_patterns, case_sensitive)


def match_path(pathname, included_patterns = None, excluded_patterns = None, case_sensitive = True):
    included = ['*'] if included_patterns is None else included_patterns
    excluded = [] if excluded_patterns is None else excluded_patterns
    return _match_path(pathname, included, excluded, case_sensitive)


def filter_paths(pathnames, included_patterns = None, excluded_patterns = None, case_sensitive = True):
    included = ['*'] if included_patterns is None else included_patterns
    excluded = [] if excluded_patterns is None else excluded_patterns
    for pathname in pathnames:
        if _match_path(pathname, included, excluded, case_sensitive):
            yield pathname


def match_any_paths(pathnames, included_patterns = None, excluded_patterns = None, case_sensitive = True):
    included = ['*'] if included_patterns is None else included_patterns
    excluded = [] if excluded_patterns is None else excluded_patterns
    for pathname in pathnames:
        if _match_path(pathname, included, excluded, case_sensitive):
            return True

    return False
