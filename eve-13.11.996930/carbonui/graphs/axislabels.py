#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\axislabels.py
import trinity
from carbonui.primitives.container import Container
import carbonui.const as uiconst

class VerticalAxisLabels(Container):
    default_name = 'verticalaxislabels'
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.maxValue = attributes.get('maxValue', 0)
        self.labelclass = attributes.get('labelClass', None)
        self.fontsize = attributes.get('fontsize', None)
        self.step = attributes.get('step', 32)
        self.count = attributes.get('count', 1)
        self.formatter = attributes.get('formatter', None)
        if not self.fontsize:
            self.fontsize = self.labelclass.default_fontsize

    def Build(self):
        width, height = self.GetAbsoluteSize()
        y = height - self.step - self.fontsize * 2 / 3
        for i in xrange(self.count):
            labelValue = self.maxValue / float(self.count) * (i + 1)
            if self.formatter:
                labelValueText = self.formatter(labelValue)
            else:
                labelValueText = str(labelValue)
            labelValueText = labelValueText
            self.labelclass(parent=self, align=uiconst.TORIGHT_NOPUSH, text=labelValueText, top=y, fontsize=self.fontsize)
            y -= self.step

    def Rebuild(self):
        self.Flush()
        self.Build()


class HorizontalAxisLabels(Container):
    default_name = 'verticalaxislabels'
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.minValue = attributes.get('minValue', 0)
        self.maxValue = attributes.get('maxValue', 0)
        self.labelclass = attributes.get('labelClass', None)
        self.fontsize = attributes.get('fontsize', None)
        self.step = attributes.get('step', 32)
        self.count = attributes.get('count', 1)
        self.formatter = attributes.get('formatter', None)
        if not self.fontsize:
            self.fontsize = self.labelclass.default_fontsize

    def Build(self):
        x = 0
        width = self.width / self.count
        halfwidth = width / 2
        valueRange = self.maxValue - self.minValue
        for i in xrange(self.count):
            labelValue = valueRange / float(self.count) * i + self.minValue
            if self.formatter:
                labelValueText = self.formatter(labelValue)
            else:
                labelValueText = str(labelValue)
            labelValueText = labelValueText
            self.labelclass(parent=self, text=labelValueText, left=x - halfwidth, top=0, width=width, height=self.fontsize, fontsize=self.fontsize)
            x += self.step

    def Rebuild(self):
        self.Flush()
        self.Build()
