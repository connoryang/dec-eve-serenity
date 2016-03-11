#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\util\uix2.py
import carbonui.const as uiconst
SEL_FILES = 0
SEL_FOLDERS = 1
SEL_BOTH = 2

def RefreshHeight(w):
    w.height = sum([ x.height for x in w.children if x.state != uiconst.UI_HIDDEN and x.align in (uiconst.TOBOTTOM, uiconst.TOTOP) ])


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('uix', locals())
