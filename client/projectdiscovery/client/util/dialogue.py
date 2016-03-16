#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\util\dialogue.py
__author__ = 'ru.Hjalti'
import math
import uicontrols
import localization
import uiprimitives
import carbonui.const as uiconst
from projectdiscovery.client import const
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold

class Dialogue(uiprimitives.Container):
    default_bgColor = (0, 0, 0, 1)

    def ApplyAttributes(self, attributes):
        super(Dialogue, self).ApplyAttributes(attributes)
        self.label = attributes.get('label')
        self.message_header_text = attributes.get('messageHeaderText')
        self.message_text = attributes.get('messageText')
        self.button_label = attributes.get('buttonLabel')
        self.toHide = attributes.get('toHide')
        self.isTutorial = attributes.get('isTutorial')
        self.toHide.opacity = 0.5
        self.construct_layout()

    def construct_layout(self):
        uicontrols.Frame(name='main_frame', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SampleBack.png', cornerSize=20, padLeft=-8, padTop=-8, padRight=-8, padBottom=-8)
        self.header_container = uiprimitives.Container(name='headerContainer', parent=self, height=25, align=uiconst.TOTOP)
        self.header_label = uicontrols.Label(parent=self.header_container, align=uiconst.CENTERLEFT, left=10, text=self.label)
        self.main_container = uiprimitives.Container(name='mainContainer', parent=self, align=uiconst.TOTOP, height=self.height - 60)
        self.agent_container = uiprimitives.Container(name='agentContainer', parent=self.main_container, align=uiconst.TOPLEFT, height=170, width=150, left=10, top=5)
        self.agent_image = uiprimitives.Sprite(name='agentImage', parent=self.agent_container, align=uiconst.TOTOP, height=150, width=150, texturePath='res:/UI/Texture/classes/ProjectDiscovery/lundberg.png')
        self.agent_label = uicontrols.Label(name='agentName', parent=self.agent_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/AgentName'), top=5)
        self.SOE_image = uiprimitives.Sprite(name='SOE_logo', parent=self.main_container, align=uiconst.BOTTOMLEFT, height=75, width=75, texturePath='res:/UI/Texture/Corps/14_128_1.png', top=-10)
        self.text_container = uiprimitives.Container(name='textContainer', parent=self.main_container, align=uiconst.TORIGHT, width=270, left=10)
        self.text_header_container = uiprimitives.Container(name='textHeaderContainer', parent=self.text_container, align=uiconst.TOTOP, height=20)
        self.header_message = EveLabelLargeBold(parent=self.text_header_container, align=uiconst.CENTERLEFT, text=self.message_header_text)
        self.main_message = uicontrols.Label(parent=self.text_container, align=uiconst.TOTOP, text=self.message_text, top=5)
        self.close_button = uicontrols.Button(name='close_button', parent=self, fontsize=14, fixedwidth=125, fixedheight=22, label=self.button_label, align=uiconst.BOTTOMRIGHT, top=10, left=10, func=lambda x: self.close())

    def close(self):
        if self.isTutorial:
            sm.ScatterEvent(const.Events.StartTutorial)
        self.toHide.opacity = 1
        sm.ScatterEvent(const.Events.EnableUI)
        self.Close()
