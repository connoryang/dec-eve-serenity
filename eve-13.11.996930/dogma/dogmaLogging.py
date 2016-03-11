#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\dogmaLogging.py
try:
    from log import LogTraceback, LogException, LogInfo, LogNotice, LogWarn, LogError
except ImportError:
    import logging
    import traceback

    def LogTraceback(msg, *args, **kwargs):
        logging.error('Traceback inbound - %s' % (msg,))
        logging.error(''.join(traceback.format_stack()))


    def LogException(msg, *args, **kwargs):
        logging.exception('Exception - %s' % (msg,))


    def __Log(logFunc, *args, **kwargs):
        logFunc(' '.join(('%s' % arg for arg in args)), **kwargs)


    def GetLogFunc(logFunc):
        return lambda *args, **kwargs: __Log(logFunc, *args, **kwargs)


    LogInfo = GetLogFunc(logging.debug)
    LogNotice = GetLogFunc(logging.info)
    LogWarn = GetLogFunc(logging.warn)
    LogError = GetLogFunc(logging.error)

import evetypes

def GetCategoryNameFromID(categoryID):
    string = evetypes.GetCategoryNameByCategory(categoryID, languageID='en')
    return plainStr(string)


def GetGroupNameFromID(groupID):
    string = evetypes.GetGroupNameByGroup(groupID, languageID='en')
    return plainStr(string)


def GetTypeNameFromID(typeID):
    string = evetypes.GetName(typeID, languageID='en')
    return plainStr(string)


def plainStr(string):
    if isinstance(string, unicode):
        return string.encode('cp1252', errors='xmlcharrefreplace')
    return string


def EvalArgs(context, *args):
    return ';'.join([ '{} = {}'.format(i, eval(i, context)) for i in args ])


def FormatDictMembers(myDict, members = None):
    if members is None:
        members = myDict
    stringParts = [ '\n  {} : {}'.format(m, repr(myDict[m])) for m in members ]
    stringParts.append('\n')
    return ''.join(stringParts)


def PrettifyString(s):
    indent = 0
    chars = []
    opener = '([{<'
    closer = ')]}>'

    def newline(chars, indent, INDENT_DEPTH = 2):
        chars.append('\n')
        for i in range(indent * INDENT_DEPTH):
            chars.append(' ')

    ignore_whitespace = True
    whitespace = ' '
    flush_separators = False
    separators = ','
    for c in s:
        if flush_separators:
            if c in separators:
                chars.append(c)
                continue
            else:
                flush_separators = False
                newline(chars, indent)
                ignore_whitespace = True
        if ignore_whitespace and c in whitespace:
            continue
        ignore_whitespace = False
        if c in opener:
            chars.append(c)
            indent += 1
            newline(chars, indent)
            ignore_whitespace = True
        elif c in closer:
            indent -= 1
            newline(chars, indent)
            chars.append(c)
            flush_separators = True
        else:
            chars.append(c)

    return ''.join(chars)


def DecodeID(someID):
    getInvItemRowFromDB = sm.GetService('i2').GetItemMx
    try:
        invItemRow = getInvItemRowFromDB(someID)
        isInvItem = True
    except:
        isInvItem = False

    if isInvItem:
        categoryName = GetCategoryNameFromID(invItemRow.categoryID)
        groupName = GetGroupNameFromID(invItemRow.groupID)
        typeName = GetTypeNameFromID(invItemRow.typeID)
        ownerID = invItemRow.ownerID
        locationID = invItemRow.locationID
        descr = 'invItem of type {}/{}/{}, ownerID {}, locationID {}'.format(categoryName, groupName, typeName, ownerID, locationID)
        return descr
    if someID in cfg.dgmattribs:
        descr = "dgmattrib '{}'".format(cfg.dgmattribs[someID].attributeName)
        return descr
    descr = '<not an invItem or dgmattrib>'
    return descr


def TraceReferrers(target, prefix = '', depth = 0, visited = None, breadthLimit = 5, depthLimit = 6):
    if depth > depthLimit:
        LogWarn(prefix, '-- bailing due to excess depth!')
        return
    if visited is None:
        visited = set()
    targetAddr = id(target)
    visited.add(targetAddr)
    import gc
    import types
    referrers = gc.get_referrers(target)
    numChildrenProcessed = 0
    for i in range(len(referrers)):
        r = referrers[i]
        if isinstance(r, types.FrameType):
            continue
        commonDescription = '{}{} : {} at {}'.format(prefix, str(i), type(r).__name__, id(r))
        if isinstance(r, dict):
            keys = r.keys()
            names = [ name for name, val in r.iteritems() if val == target ]
            LogWarn(commonDescription, 'via', names, 'of', keys)
        else:
            LogWarn(commonDescription)
        valString = str(r)
        if len(valString) > 200:
            LogWarn('  value (truncated):', valString[:200])
        else:
            LogWarn('  value:', r)
        if id(r) in visited:
            LogWarn('  -- already visited')
            continue
        if numChildrenProcessed == breadthLimit:
            LogWarn('  -- truncating due to breadthLimit of', breadthLimit)
            break
        referrers[i] = 'removed'
        TraceReferrers(r, prefix=prefix + str(i) + '.', depth=depth + 1, visited=visited, depthLimit=depthLimit)
        numChildrenProcessed += 1


def WrappedMethod(m):
    return m


def WrappedClass(m):
    return m
