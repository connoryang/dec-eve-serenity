#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\util\various_unsorted.py
import log
import blue
import sys
from functools import wraps
import telemetry

def GetBuffersize(size):
    if size <= 8:
        return 8
    if size <= 16:
        return 16
    if size <= 32:
        return 32
    if size <= 64:
        return 64
    if size <= 128:
        return 128
    if size <= 256:
        return 256
    if size <= 512:
        return 512
    if size <= 1024:
        return 1024
    if size <= 2048:
        return 2048
    return 128


def StringColorToHex(color):
    colors = {'Black': '0xff000000',
     'Green': '0xff008000',
     'Silver': '0xffC0C0C0',
     'Lime': '0xff00FF00',
     'Gray': '0xff808080',
     'Grey': '0xff808080',
     'Olive': '0xff808000',
     'White': '0xffFFFFFF',
     'Yellow': '0xffFFFF00',
     'Maroon': '0xff800000',
     'Navy': '0xff000080',
     'Red': '0xffFF0000',
     'Blue': '0xff0000FF',
     'Purple': '0xff800080',
     'Teal': '0xff008080',
     'Fuchsia': '0xffFF00FF',
     'Aqua': '0xff00FFFF',
     'Orange': '0xffFF8000',
     'Transparent': '0x00000000',
     'Lightred': '0xffcc3333',
     'Lightblue': '0xff7777ff',
     'Lightgreen': '0xff80ff80'}
    return colors.get(color.capitalize(), None)


def Sort(lst):
    lst.sort(lambda x, y: cmp(str(x).upper(), str(y).upper()))
    return lst


def SortListOfTuples(lst, reverse = 0):
    lst = sorted(lst, reverse=reverse, key=lambda data: data[0])
    return [ item[1] for item in lst ]


def SortByAttribute(lst, attrname = 'name', idx = None, reverse = 0):
    newlst = []
    for item in lst:
        if idx is None:
            newlst.append((getattr(item, attrname, None), item))
        else:
            newlst.append((getattr(item[idx], attrname, None), item))

    ret = SortListOfTuples(newlst, reverse)
    return ret


def SmartCompare(x, y, sortOrder):
    for column, direction in sortOrder:
        if direction == 1:
            if x[0][column] > y[0][column]:
                return 1
            if x[0][column] < y[0][column]:
                return -1
        else:
            if x[0][column] < y[0][column]:
                return 1
            if x[0][column] > y[0][column]:
                return -1

    return 0


def FindChild(fromParent, *names):
    return fromParent.FindChild(*names)


def GetChild(parent, *names):
    return parent.GetChild(*names)


def FindChildByClass(parent, classes = (), searchIn = [], withAttributes = []):
    children = []
    for each in searchIn:
        for w in parent.Find(each):
            if isinstance(w, classes):
                if withAttributes:
                    for attrTuple in withAttributes:
                        attr, value = attrTuple
                        if getattr(w, attr, None) == value:
                            children.append(w)

                else:
                    children.append(w)

    return children


@telemetry.ZONE_METHOD
def SetOrder(child, idx = 0):
    child.SetOrder(idx)


def GetIndex(item):
    if item.parent:
        return item.parent.children.index(item)
    return 0


def Flush(parent):
    parent.Flush()


def FlushList(lst):
    for each in lst[:]:
        if each is not None and not getattr(each, 'destroyed', 0):
            each.Close()

    del lst[:]


def GetWindowAbove(item):
    if item == uicore.desktop:
        return None
    if uicore.registry.IsWindow(item) and not getattr(item, 'isImplanted', False):
        return item
    if item.parent and not item.parent.destroyed:
        return GetWindowAbove(item.parent)


def GetDesktopObject(item):
    if not item.parent:
        if item.destroyed:
            return None
        else:
            return item
    else:
        return GetDesktopObject(item.parent)


def GetBrowser(item):
    if item == uicore.desktop:
        return
    if getattr(item, 'IsBrowser', None):
        return item
    from carbonui.control.edit import EditCore
    if isinstance(item, EditCore):
        return item
    if item.parent:
        return GetBrowser(item.parent)


def GetAttrs(obj, *names):
    for name in names:
        obj = getattr(obj, name, None)
        if obj is None:
            return

    return obj


def Transplant(wnd, newParent, idx = None):
    if wnd is None or wnd.destroyed or newParent is None or newParent.destroyed:
        return
    if idx in (-1, None):
        idx = len(newParent.children)
    wnd.SetParent(newParent, idx)


def IsClickable(wnd):
    return wnd.IsClickable()


def IsUnder(child, ancestor_maybe, retfailed = False):
    return child.IsUnder(ancestor_maybe, retfailed)


def IsVisible(item):
    return item.IsVisible()


def MapIcon(sprite, iconPath, ignoreSize = 0):
    if hasattr(sprite, 'LoadIcon'):
        return sprite.LoadIcon(iconPath, ignoreSize)
    print 'Someone load icon to non icon class', sprite, iconPath
    import uicontrols
    return uicontrols.Icon.LoadIcon(sprite, iconPath, ignoreSize)


def ConvertDecimal(qty, fromChar, toChar, numDecimals = None):
    import types
    ret = qty
    if type(ret) in [types.IntType, types.FloatType, types.LongType]:
        if numDecimals is not None:
            ret = '%.*f' % (numDecimals, qty)
        else:
            ret = repr(qty)
    ret = ret.replace(fromChar, toChar)
    return ret


def GetClipboardData():
    import blue
    try:
        return blue.win32.GetClipboardUnicode()
    except blue.error:
        return ''


def GetTrace(item, trace = '', div = '/'):
    trace = div + item.name + trace
    if getattr(item, 'parent', None) is None:
        return trace
    return GetTrace(item.parent, trace, div)


def ParseHTMLColor(colorstr, asTuple = 0, error = 0):
    colors = {'Black': '0x000000',
     'Green': '0x008000',
     'Silver': '0xC0C0C0',
     'Lime': '0x00FF00',
     'Gray': '0x808080',
     'Grey': '0x808080',
     'Olive': '0x808000',
     'White': '0xFFFFFF',
     'Yellow': '0xFFFF00',
     'Maroon': '0x800000',
     'Navy': '0x000080',
     'Red': '0xFF0000',
     'Blue': '0x0000FF',
     'Purple': '0x800080',
     'Teal': '0x008080',
     'Fuchsia': '0xFF00FF',
     'Aqua': '0x00FFFF',
     'Transparent': '0x00000000'}
    try:
        colorstr = colors.get(colorstr.capitalize(), colorstr).lower()
    except:
        sys.exc_clear()
        return colorstr

    if colorstr.startswith('#'):
        colorstr = colorstr.replace('#', '0x')
    r, g, b, a = (0.0, 255.0, 0.0, 255.0)
    if colorstr.startswith('0x'):
        try:
            if len(colorstr) == 8:
                r = eval('0x' + colorstr[2:4])
                g = eval('0x' + colorstr[4:6])
                b = eval('0x' + colorstr[6:8])
            elif len(colorstr) == 10:
                a = eval('0x' + colorstr[2:4])
                r = eval('0x' + colorstr[4:6])
                g = eval('0x' + colorstr[6:8])
                b = eval('0x' + colorstr[8:10])
            else:
                log.LogWarn('Invalid color string, has to be in form of 0xffffff or 0xffffffff (with alpha). 0x can be replaced with # (%s)' % colorstr)
                if error:
                    return
        except:
            log.LogWarn('Invalid color string, has to be in form of 0xffffff or 0xffffffff (with alpha). 0x can be replaced with # (%s)' % colorstr)
            if error:
                return

    else:
        log.LogError('Unknown color (' + colorstr + '), I only know: ' + strx(', '.join(colors.keys())))
        if error:
            return
    col = (r / 255.0,
     g / 255.0,
     b / 255.0,
     a / 255.0)
    if asTuple:
        return col
    import trinity
    return trinity.TriColor(*col)


def GetFormWindow(caption = None, buttons = None, okFunc = None, windowClass = None):
    import carbonui.const as uiconst
    from carbonui.control.window import WindowCoreOverride as Window
    windowClass = windowClass or Window
    wnd = windowClass(parent=uicore.layer.main, width=256, height=128)
    if caption is not None:
        wnd.SetCaption(caption)
    wnd.confirmCheckControls = []
    wnd.SetButtons(buttons or uiconst.OKCANCEL, okFunc=ConfirmFormWindow)
    return wnd


def AddFormControl(wnd, control, key, retval = None, required = False, errorcheck = None):
    wnd.confirmCheckControls.append((control,
     key,
     retval,
     required,
     errorcheck))


def AddFormErrorCheck(wnd, errorCheck):
    wnd.errorCheck = errorCheck


def ConfirmFormWindow(sender, *args):
    import carbonui.const as uiconst
    uicore.registry.SetFocus(uicore.desktop)
    if sender is None:
        if getattr(uicore.registry.GetFocus(), 'stopconfirm', 0):
            return
    wnd = GetWindowAbove(sender)
    result = {}
    for each in getattr(wnd, 'confirmCheckControls', []):
        control, key, retval, required, check = each
        checkValue = control.GetValue()
        if required:
            if checkValue is None or checkValue == '':
                uicore.Message('MissingRequiredField', {'fieldname': key})
                return
        if check:
            hint = check(checkValue)
            if hint == 'silenterror':
                return
            if hint:
                uicore.Message('CustomInfo', {'info': hint})
                return
        if type(retval) == dict:
            result.update(retval)
            continue
        result[key] = checkValue

    if not result:
        return
    formErrorCheck = getattr(wnd, 'errorCheck', None)
    if formErrorCheck:
        if formErrorCheck:
            hint = formErrorCheck(result)
            if hint == 'silenterror':
                return
            if hint:
                uicore.Message('CustomInfo', {'info': hint})
                return
    wnd.result = result
    if uicore.registry.GetModalWindow() == wnd:
        wnd.SetModalResult(uiconst.ID_OK)
    else:
        if wnd.sr.queue:
            wnd.sr.queue.put(result)
        wnd.SetModalResult(uiconst.ID_OK)
        return result


def AskAmount(caption = None, question = None, setvalue = '', intRange = None, floatRange = None):
    import carbonui.const as uiconst
    from carbonui.control.singlelineedit import SinglelineEditCoreOverride as SinglelineEdit
    from carbonui.control.label import LabelOverride as Label
    if caption is None:
        caption = 'How much?'
    if question is None:
        question = 'How much?'
    wnd = GetFormWindow(caption)
    if question:
        Label(parent=wnd.sr.content, text=question, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
    edit = SinglelineEdit(parent=wnd.sr.content, ints=intRange, floats=floatRange, setvalue=setvalue)
    AddFormControl(wnd, edit, 'amount', retval=None, required=True, errorcheck=None)
    if wnd.ShowModal() == uiconst.ID_OK:
        return wnd.result


def AskName(caption = None, label = None, setvalue = '', maxLength = None, passwordChar = None, validator = None):
    import carbonui.const as uiconst
    import localization
    from carbonui.control.singlelineedit import SinglelineEditCoreOverride as SinglelineEdit
    from carbonui.control.label import LabelOverride as Label
    if caption is None:
        caption = localization.GetByLabel('UI/Common/Name/TypeInName')
    if label is None:
        label = localization.GetByLabel('UI/Common/Name/TypeInName')
    wnd = GetFormWindow(caption)
    if label:
        Label(parent=wnd.sr.content, text=label, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
    edit = SinglelineEdit(parent=wnd.sr.content, maxLength=maxLength, setvalue=setvalue)
    AddFormControl(wnd, edit, 'name', retval=None, required=True, errorcheck=validator or NamePopupErrorCheck)
    if wnd.ShowModal() == uiconst.ID_OK:
        return wnd.result


def AskChoice(caption = '', question = '', choices = [], modal = False):
    import carbonui.const as uiconst
    from carbonui.control.buttons import ButtonCoreOverride as Button
    from carbonui.control.scroll import ScrollCoreOverride as Scroll
    from carbonui.control.checkbox import CheckboxCoreOverride as Checkbox
    from carbonui.control.label import LabelOverride as Label
    wnd = GetFormWindow(caption)
    if question:
        label = Label(parent=wnd.sr.content, text=question, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
        wnd.SetMinSize((label.width + 20, wnd.GetMinHeight()))
    combo = Combo(parent=wnd.sr.content, options=choices, align=uiconst.TOTOP)
    AddFormControl(wnd, combo, 'choice', retval=None, required=True, errorcheck=None)
    if modal:
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
    elif wnd.ShowDialog() == uiconst.ID_OK:
        return wnd.result


def NamePopupErrorCheck(name):
    if not len(name) or len(name) and len(name.strip()) < 1:
        return localization.GetByLabel('UI/Common/Name/PleaseTypeSomething')
    return ''


def ParanoidDecoMethod(fn, attrs):
    check = []
    if attrs is None:
        check = ['sr']
    else:
        check.extend(attrs)

    @wraps(fn)
    def deco(self, *args, **kw):
        if GetAttrs(self, *check) is None:
            return
        if self.destroyed:
            return
        return fn(self, *args, **kw)

    return deco


def NiceFilter(func, list):
    ret = []
    for x in list:
        if func(x):
            ret.append(x)
        blue.pyos.BeNice()

    return ret


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('uiutil', locals())
