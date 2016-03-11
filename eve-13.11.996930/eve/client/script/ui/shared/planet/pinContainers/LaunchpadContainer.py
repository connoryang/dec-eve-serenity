#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\planet\pinContainers\LaunchpadContainer.py
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import Label
import uiprimitives
import util
import localization
from .BasePinContainer import BasePinContainer
from .StorageFacilityContainer import StorageFacilityContainer
from .. import planetCommon

class LaunchpadContainer(StorageFacilityContainer):
    __guid__ = 'planet.ui.LaunchpadContainer'
    default_name = 'LaunchpadContainer'

    def ApplyAttributes(self, attributes):
        BasePinContainer.ApplyAttributes(self, attributes)

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_LAUNCH, panelCallback=self.PanelLaunch), util.KeyVal(id=planetCommon.PANEL_STORAGE, panelCallback=self.PanelShowStorage)]
        btns.extend(BasePinContainer._GetActionButtons(self))
        return btns

    def PanelLaunch(self):
        bp = sm.GetService('michelle').GetBallpark()
        text = None
        if bp is not None and not self.pin.IsInEditMode():
            customsOfficeIDs = sm.GetService('planetInfo').GetOrbitalsForPlanet(sm.GetService('planetUI').planetID, const.groupPlanetaryCustomsOffices)
            if len(customsOfficeIDs) > 0:
                try:
                    customsOfficeID = None
                    for ID in customsOfficeIDs:
                        customsOfficeID = ID
                        break

                    sm.GetService('planetUI').OpenPlanetCustomsOfficeImportWindow(customsOfficeID, self.pin.id)
                    self.CloseByUser()
                    return
                except UserError as e:
                    if e.msg == 'ShipCloaked':
                        text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadWhileCloaked')
                    else:
                        message = cfg.GetMessage(e.msg)
                        text = message.text

        if text is None:
            if self.pin.IsInEditMode():
                text = localization.GetByLabel('UI/PI/Common/CustomsOfficeNotBuilt')
            else:
                solarSystemID = sm.GetService('planetUI').GetCurrentPlanet().solarSystemID
                if solarSystemID == session.locationid:
                    text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadNotThere')
                else:
                    text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadLocation')
        return Label(parent=self.actionCont, text=text, align=uiconst.TOTOP)
