#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\buyButton.py
from eve.client.script.ui.shared.skins.event import LogBuySkinAur, LogBuySkinIsk
from eve.client.script.ui.shared.vgs.button import BuyButtonAurSmall, BuyButtonIskSmall
import localization
import evetypes

class SkinLicenseBuyButtonAur(BuyButtonAurSmall):

    def ApplyAttributes(self, attributes):
        self.logContext = attributes.logContext
        super(SkinLicenseBuyButtonAur, self).ApplyAttributes(attributes)

    def OpenOfferWindow(self):
        super(SkinLicenseBuyButtonAur, self).OpenOfferWindow()
        LogBuySkinAur(None, None, self.logContext)


class SkinLicenseBuyButtonIsk(BuyButtonIskSmall):

    def ApplyAttributes(self, attributes):
        super(SkinLicenseBuyButtonIsk, self).ApplyAttributes(attributes)
        self.logContext = attributes.logContext

    def OpenMarketWindow(self):
        super(SkinLicenseBuyButtonIsk, self).OpenMarketWindow()
        LogBuySkinIsk(None, None, self.logContext)


class SkinMaterialBuyButtonAur(BuyButtonAurSmall):

    def ApplyAttributes(self, attributes):
        self.typeID = attributes.typeID
        self.materialID = attributes.materialID
        self.logContext = attributes.logContext
        attributes.types = self.GetLicenseTypesForMaterial
        super(SkinMaterialBuyButtonAur, self).ApplyAttributes(attributes)

    def GetLicenseTypesForMaterial(self):
        skinSvc = sm.GetService('skinSvc')
        licenses = skinSvc.static.GetLicensesForTypeWithMaterial(self.typeID, self.materialID)
        return [ l.licenseTypeID for l in licenses ]

    def OpenOfferWindow(self):
        super(SkinMaterialBuyButtonAur, self).OpenOfferWindow()
        LogBuySkinAur(self.typeID, self.materialID, self.logContext)


class SkinMaterialBuyButtonIsk(BuyButtonIskSmall):

    def ApplyAttributes(self, attributes):
        super(SkinMaterialBuyButtonIsk, self).ApplyAttributes(attributes)
        self.materialID = attributes.materialID
        self.logContext = attributes.logContext

    def OpenMarketWindow(self):
        shipName = evetypes.GetName(self.typeID)
        material = sm.GetService('skinSvc').GetStaticMaterialByID(self.materialID)
        searchString = localization.GetByLabel('UI/Skins/MarketSearchTemplate', shipName=shipName, materialName=material.name)
        from eve.client.script.ui.shared.market.marketbase import RegionalMarket
        RegionalMarket.OpenAndSearch(searchString)
        LogBuySkinIsk(self.typeID, self.materialID, self.logContext)
