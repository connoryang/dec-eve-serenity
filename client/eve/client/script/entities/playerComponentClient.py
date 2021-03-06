#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\entities\playerComponentClient.py
import util
import svc
import localization

class EvePlayerComponentClient(svc.playerComponentClient):
    __guid__ = 'svc.EvePlayerComponentClient'
    __replaceservice__ = 'playerComponentClient'

    def RegisterComponent(self, entity, component):
        if entity.entityID != session.charid:
            ctx = entity.GetComponent('contextMenu')
            if ctx:
                if util.IsCharacter(entity.entityID):
                    ctx.AddMenuEntry(localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo)

    def ShowInfo(self, entityID):
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(entityID).typeID, entityID)
