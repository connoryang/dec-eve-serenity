#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assetsSearch.py
from eveAssets.assetSearchUtil import IsPartOfText, IsTextMatch, ParseString
import uiprimitives
import uicontrols
import carbonui.const as uiconst
import base
import localization

class SearchBox(uicontrols.SinglelineEdit):
    __guid__ = 'assets.SearchBox'
    default_dynamicHistoryWidth = True

    def ApplyAttributes(self, attributes):
        uicontrols.SinglelineEdit.ApplyAttributes(self, attributes)
        self.blockSetValue = True
        self.TEXTRIGHTMARGIN = 1
        self.searchKeywords = attributes.get('keywords', [])
        self.CreateLayout()

    def SetValue(self, text, *args, **kwargs):
        oldText = self.GetValue()
        uicontrols.SinglelineEdit.SetValue(self, text, *args, **kwargs)
        self.caretIndex = self.GetCursorFromIndex(self.GetSmartCaretIndex(oldText, text))
        self.RefreshCaretPosition()

    def GetSmartCaretIndex(self, oldText, newText):
        oldText = oldText[::-1]
        newText = newText[::-1]
        for i in xrange(len(oldText)):
            if oldText[i] != newText[i]:
                return len(newText) - i

        return len(newText)

    def CreateLayout(self):
        self.optionIcon = uiprimitives.Sprite(parent=self.sr.maincontainer, name='options', texturePath='res:/UI/Texture/Icons/38_16_229.png', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, idx=0, hint=localization.GetByLabel('UI/Inventory/AssetSearch/KeywordOptionsHint'))
        self.optionIcon.SetAlpha(0.8)
        self.optionIcon.OnClick = self.OnOptionClick

    def OnOptionClick(self):
        self.ShowHistoryMenu(self.GetStaticHints())

    def GetStaticHints(self):
        currentText = self.GetValue(registerHistory=0)
        currentText = currentText.rstrip()
        if currentText:
            currentText += ' '
        hints = []
        for kw in self.searchKeywords:
            hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/KeywordHint', keyword=kw.keyword, description=kw.optionDescription), '%s%s: ' % (currentText, kw.keyword)))

        return hints

    def GetDynamicHints(self):
        hints = []
        caretIndex = self.caretIndex[0]
        currentText = self.GetValue(registerHistory=0)
        headText, tailText = currentText[:caretIndex], currentText[caretIndex:]
        tailText = tailText.lstrip()
        trimmedText = headText.rstrip()
        if trimmedText.endswith(':'):
            strippedText, lastWord = self.SplitText(trimmedText, removeSeprator=True)
            if lastWord:
                for kw in self.IterMatchingKeywords(lastWord):
                    if kw.specialOptions:
                        for option in kw.specialOptions:
                            hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/OptionHint', keyword=kw.keyword, option=option), '%s%s: %s %s' % (strippedText,
                              kw.keyword,
                              option,
                              tailText)))

        else:
            strippedText, lastWord = self.SplitText(trimmedText, removeSeprator=False)
            freeText, matches = ParseString(trimmedText)
            if lastWord:
                if matches and IsTextMatch(lastWord, matches[-1][1]):
                    keyword, value = matches[-1]
                    for kw in self.IterMatchingKeywords(keyword):
                        if kw.specialOptions:
                            for option in kw.specialOptions:
                                if IsPartOfText(option, value):
                                    hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/OptionHint', keyword=kw.keyword, option=option), '%s%s %s' % (strippedText, option, tailText)))

                            break

                else:
                    for kw in self.IterMatchingKeywords(lastWord):
                        hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/KeywordHint', keyword=kw.keyword, description=kw.optionDescription), '%s%s: %s' % (strippedText, kw.keyword, tailText)))

        return hints

    def IterMatchingKeywords(self, keyword):
        for kw in self.searchKeywords:
            if IsPartOfText(kw.keyword, keyword):
                yield kw

    def SplitText(self, baseText, removeSeprator = False):
        strippedText, lastWord = (None, None)
        parts = baseText.split()
        if parts:
            lastWord = parts[-1]
            strippedText = baseText[:-len(lastWord)]
            if removeSeprator:
                lastWord = lastWord[:-1]
            if strippedText:
                strippedText = strippedText.rstrip() + ' '
        return (strippedText, '' if lastWord is None else lastWord.lower())

    def TryRefreshHistory(self, currentString):
        self.refreshHistoryTimer = base.AutoTimer(200, self.TryRefreshHistory_Thread, currentString)

    def TryRefreshHistory_Thread(self, currentString):
        if currentString.rstrip().endswith(':'):
            self.CheckHistory()
        self.refreshHistoryTimer = None

    def OnHistoryClick(self, clickedString):
        self.TryRefreshHistory(clickedString)

    def OnComboChange(self, combo, label, value, *args):
        self.SetValue(label, updateIndex=0)
        self.TryRefreshHistory(value)

    def GetValid(self):
        valid = uicontrols.SinglelineEdit.GetValid(self)
        history = [ (text, text) for text in valid ]
        hints = self.GetDynamicHints()
        return hints + history

    def Confirm(self, *args):
        active = getattr(self, 'active', None)
        if active:
            text = active.string
            self.SetValue(text)
        uicontrols.SinglelineEdit.Confirm(self, *args)
        if active:
            self.TryRefreshHistory(text)
