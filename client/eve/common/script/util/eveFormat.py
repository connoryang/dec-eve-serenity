#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\eveFormat.py
import math
import sys
from carbon.common.script.util.format import DECIMAL, FmtAmt
import evetypes
import log
import eve.common.lib.appConst as const
import eve.common.script.mgt.appLogConst as logConst
import localization
PROBE_STATE_TEXT_MAP = {const.probeStateInactive: 'UI/Inflight/Scanner/Inactive',
 const.probeStateIdle: 'UI/Inflight/Scanner/Idle',
 const.probeStateMoving: 'UI/Inflight/Scanner/Moving',
 const.probeStateWarping: 'UI/Inflight/Scanner/Warping',
 const.probeStateScanning: 'UI/Inflight/Scanner/Scanning',
 const.probeStateReturning: 'UI/Inflight/Scanner/Returning'}
PROBE_STATE_COLOR_MAP = {const.probeStateInactive: '<color=gray>%s</color>',
 const.probeStateIdle: '<color=0xFF22FF22>%s</color>',
 const.probeStateMoving: '<color=yellow>%s</color>',
 const.probeStateWarping: '<color=yellow>%s</color>',
 const.probeStateScanning: '<color=0xFF66BBFF>%s</color>',
 const.probeStateReturning: '<color=yellow>%s</color>'}
CURRENCY_FORMAT_TRANSLATIONS = {(const.creditsAURUM, 0): 'UI/Util/FmtAurNoDecimal',
 (const.creditsAURUM, 1): 'UI/Util/FmtAur',
 (const.creditsISK, 0): 'UI/Util/FmtIskNoDecimal',
 (const.creditsISK, 1): 'UI/Util/FmtIsk'}

def FmtISK(isk, showFractionsAlways = 1):
    return FmtCurrency(isk, showFractionsAlways, const.creditsISK)


def FmtAUR(aur, showFractionsAlways = 0):
    return FmtCurrency(aur, showFractionsAlways, const.creditsAURUM)


def FmtISKAndRound(isk, showFractionsAlways = 1):
    return FmtISK(RoundISK(isk), showFractionsAlways)


def RoundISK(isk):
    if isk < 10:
        return round(isk, 2)
    elif isk < 100:
        return round(isk, 1)
    elif isk < 1000:
        return round(isk, 0)
    elif isk < 10000:
        return round(isk, -1)
    elif isk < 100000:
        return round(isk, -2)
    elif isk < 1000000:
        return round(isk, -3)
    elif isk < 10000000:
        return round(isk, -4)
    elif isk < 100000000:
        return round(isk, -5)
    else:
        return round(isk, -6)


def FmtCurrency(amount, showFractionsAlways = 1, currency = None):
    if currency is None:
        key = (const.creditsISK, showFractionsAlways)
    else:
        key = (currency, showFractionsAlways)
    fmtPath = CURRENCY_FORMAT_TRANSLATIONS[key]
    if not showFractionsAlways:
        amount = int(amount)
    return localization.GetByLabel(fmtPath, amount=amount)


def FmtRef(entryTypeID, o1, o2, arg1, pretty = 1, amount = 0.0):
    if entryTypeID == const.refBackwardCompatible:
        if pretty:
            return ''
        else:
            return localization.GetByLabel('UI/Generic/FormatReference/backwardsCompatiable', type=entryTypeID, o1=o1, o2=o2, arg=arg1)
    if entryTypeID == const.refUndefined:
        if pretty:
            return ''
        else:
            return localization.GetByLabel('UI/Generic/FormatReference/undefinedType', type=entryTypeID, o1=o1, o2=o2, arg=arg1)
    else:
        if entryTypeID == const.refPlayerTrading:
            return localization.GetByLabel('UI/Generic/FormatReference/directTradeBetweenPlayers', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refMarketTransaction:
            return localization.GetByLabel('UI/Generic/FormatReference/marketBoughtStuff', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refMarketFinePaid:
            return localization.GetByLabel('UI/Generic/FormatReference/marketpaidFine')
        if entryTypeID == const.refGMCashTransfer:
            return localization.GetByLabel('UI/Generic/FormatReference/gmIssuedTransaction', arg=arg1, name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refMissionReward:
            return localization.GetByLabel('UI/Generic/FormatReference/missionReward')
        if entryTypeID == const.refCloneActivation:
            return localization.GetByLabel('UI/Generic/FormatReference/cloneActivated')
        if entryTypeID == const.refCloneTransfer:
            return localization.GetByLabel('UI/Generic/FormatReference/cloneTransferTo', arg=arg1)
        if entryTypeID == const.refInheritance:
            return localization.GetByLabel('UI/Generic/FormatReference/inheritance', name=GetName(o1))
        if entryTypeID == const.refPlayerDonation:
            return localization.GetByLabel('UI/Generic/FormatReference/playerDonation', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refCorporationPayment:
            if arg1 != -1:
                return localization.GetByLabel('UI/Generic/FormatReference/corpPayment1', arg=GetName(arg1), name1=GetName(o1), name2=GetName(o2))
            return localization.GetByLabel('UI/Generic/FormatReference/corpPayment2', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refDockingFee:
            return localization.GetByLabel('UI/Generic/FormatReference/dockingFee', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refOfficeRentalFee:
            return localization.GetByLabel('UI/Generic/FormatReference/officeRentalFee', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refFactorySlotRentalFee:
            return localization.GetByLabel('UI/Generic/FormatReference/factoryRentalFee', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentMiscellaneous:
            return localization.GetByLabel('UI/Generic/FormatReference/cashFromAgent', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentMissionReward:
            return localization.GetByLabel('UI/Generic/FormatReference/missionRewardFromAgent', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentMissionTimeBonusReward:
            return localization.GetByLabel('UI/Generic/FormatReference/missionRewardBonusFromAgent', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentMissionCollateralPaid:
            return localization.GetByLabel('UI/Generic/FormatReference/missionCollateralPaid', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentMissionCollateralRefunded:
            return localization.GetByLabel('UI/Generic/FormatReference/missionCollateralRefund', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentDonation:
            return localization.GetByLabel('UI/Generic/FormatReference/agentDonation', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentSecurityServices:
            return localization.GetByLabel('UI/Generic/FormatReference/concordRelations', name1=GetName(o1), name2=GetName(o2))
        if entryTypeID == const.refAgentLocationServices:
            return localization.GetByLabel('UI/Generic/FormatReference/agentLocationService')
        if entryTypeID == const.refCSPA:
            if arg1:
                return localization.GetByLabel('UI/Generic/FormatReference/cspaServiceChargePaidBy', name1=GetName(o1), name2=GetName(arg1))
            else:
                return localization.GetByLabel('UI/Generic/FormatReference/cspaServiceCharge', name=GetName(o1))
        elif entryTypeID == const.refCSPAOfflineRefund:
            if arg1:
                return localization.GetByLabel('UI/Generic/FormatReference/cspaServiceChargeRefundBy', name1=GetName(o2), name2=GetName(arg1))
            else:
                return localization.GetByLabel('UI/Generic/FormatReference/cspaServiceChargeRefundByConcord', name1=GetName(o2))
        else:
            if entryTypeID == const.refBountySurcharge:
                return localization.GetByLabel('UI/Generic/FormatReference/incursionBountySurcharge')
            if entryTypeID == const.refRepairBill:
                return localization.GetByLabel('UI/Generic/FormatReference/repairBill', name1=GetName(o1), name2=GetName(o2))
            if entryTypeID == const.refBounty:
                return localization.GetByLabel('UI/Generic/FormatReference/bountyPaidTo', name1=GetName(o1), name2=GetName(arg1))
            if entryTypeID == const.refBountyReimbursement:
                return localization.GetByLabel('UI/Generic/FormatReference/bountyReimbursed')
            if entryTypeID == const.refBountyPrize:
                if arg1 == -1:
                    return localization.GetByLabel('UI/Generic/FormatReference/bountyKilledMultipleEntities', name1=GetName(o2))
                else:
                    return localization.GetByLabel('UI/Generic/FormatReference/bountyKilledHim', name1=GetName(o2), name2=GetName(arg1))
            else:
                if entryTypeID == const.refBountyPrizes:
                    return localization.GetByLabel('UI/Generic/FormatReference/bountyPrizes', location=GetLocation(arg1) or cfg.evelocations.Get(arg1).name, name1=GetName(o2))
                if entryTypeID == const.refKillRightBuy:
                    return localization.GetByLabel('UI/Generic/FormatReference/killRightFee', buyer=GetName(o1), seller=GetName(o2), name=GetName(arg1))
                if entryTypeID == const.refInsurance:
                    if arg1 > 0:
                        return localization.GetByLabel('UI/Generic/FormatReference/insurancePaidByCoveringLoss', itemname=evetypes.GetName(arg1), name1=GetName(o1), name2=GetName(o2))
                    elif arg1 and arg1 < 0:
                        return localization.GetByLabel('UI/Generic/FormatReference/insurancePaidForShip', location=GetLocation(-arg1), name1=GetName(o1), name2=GetName(o2), refID=-arg1)
                    else:
                        return localization.GetByLabel('UI/Generic/FormatReference/insurancePaidTo', name1=GetName(o1), name2=GetName(o2))
                else:
                    if entryTypeID == const.refDatacoreFee:
                        return localization.GetByLabel('UI/Generic/FormatReference/datacoreFee')
                    if entryTypeID == const.refSecurityTagProcessingFee:
                        return localization.GetByLabel('UI/Generic/FormatReference/SecurityTagProcessingFee')
                    if entryTypeID == const.refMissionExpiration:
                        return localization.GetByLabel('UI/Generic/FormatReference/missionRollebackExpired')
                    if entryTypeID == const.refMissionCompletion:
                        return localization.GetByLabel('UI/Generic/FormatReference/missionComplete')
                    if entryTypeID == const.refShares:
                        return localization.GetByLabel('UI/Generic/FormatReference/sharesTransaction')
                    if entryTypeID == const.refCourierMissionEscrow:
                        return localization.GetByLabel('UI/Generic/FormatReference/missionCourierEscrow')
                    if entryTypeID == const.refMissionCost:
                        return localization.GetByLabel('UI/Generic/FormatReference/missionCost')
                    if entryTypeID == const.refCorporationTaxNpcBounties:
                        return localization.GetByLabel('UI/Generic/FormatReference/corpTaxBounties')
                    if entryTypeID == const.refCorporationTaxAgentRewards:
                        return localization.GetByLabel('UI/Generic/FormatReference/corpTaxMissions')
                    if entryTypeID == const.refCorporationTaxAgentBonusRewards:
                        return localization.GetByLabel('UI/Generic/FormatReference/corpTaxMissionBonus')
                    if entryTypeID == const.refCorporationTaxRewards:
                        return localization.GetByLabel('UI/Generic/FormatReference/corpTaxRewards', name=GetName(o1))
                    if entryTypeID == const.refCorporationAccountWithdrawal:
                        return localization.GetByLabel('UI/Generic/FormatReference/corpWithdrawl', name1=GetName(arg1), name2=GetName(o1), name3=GetName(o2))
                    if entryTypeID == const.refCorporationDividendPayment:
                        if o2 == const.ownerBank:
                            return localization.GetByLabel('UI/Generic/FormatReference/corpDividendsPayed', name=GetName(o1))
                        else:
                            return localization.GetByLabel('UI/Generic/FormatReference/corpDividendsPayedFrom', name1=GetName(o2), name2=GetName(arg1))
                    else:
                        if entryTypeID == const.refCorporationRegistrationFee:
                            return localization.GetByLabel('UI/Generic/FormatReference/corpRegistrationFee', name1=GetName(o1))
                        if entryTypeID == const.refCorporationLogoChangeCost:
                            return localization.GetByLabel('UI/Generic/FormatReference/corpLogoChangeFee', name1=GetName(o1), name2=GetName(arg1))
                        if entryTypeID == const.refCorporationAdvertisementFee:
                            return localization.GetByLabel('UI/Generic/FormatReference/corpAdvertisementFee', name1=GetName(o1))
                        if entryTypeID == const.refReleaseOfImpoundedProperty:
                            return localization.GetByLabel('UI/Generic/FormatReference/releaseImpoundFee', location=GetLocation(arg1), name1=GetName(o1), name2=GetName(o2))
                        if entryTypeID == const.refBrokerfee:
                            owner = cfg.eveowners.GetIfExists(o1)
                            if owner is not None:
                                return localization.GetByLabel('UI/Generic/FormatReference/marketBrokersFeeBy', name1=owner.ownerName)
                            return localization.GetByLabel('UI/Generic/FormatReference/marketBrokersFee')
                        if entryTypeID == const.refMarketEscrow:
                            owner = cfg.eveowners.GetIfExists(o1 if arg1 == -1 else o2)
                            if owner is not None:
                                if amount < 0.0:
                                    return localization.GetByLabel('UI/Generic/FormatReference/marketEscrowAuthorizedBy', name=owner.ownerName)
                            if amount < 0.0:
                                return localization.GetByLabel('UI/Generic/FormatReference/marketEscrow')
                            else:
                                return localization.GetByLabel('UI/Generic/FormatReference/marketEscrowRelease')
                        else:
                            if entryTypeID == const.refWarFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/warFee', name=GetName(arg1))
                            if entryTypeID == const.refAllianceRegistrationFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/allianceRegistrationFee')
                            if entryTypeID == const.refAllianceMaintainanceFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/allianceMaintenceFee', name=GetName(arg1))
                            if entryTypeID == const.refSovereignityRegistrarFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/sovereigntyRegistrarFee', name=GetLocation(arg1))
                            if entryTypeID == const.refInfrastructureHubBill:
                                return localization.GetByLabel('UI/Generic/FormatReference/infrastructureHubBillRef', name=GetLocation(arg1))
                            if entryTypeID == const.refSovereignityUpkeepAdjustment:
                                return localization.GetByLabel('UI/Generic/FormatReference/sovereigntyAdjustmentFee', name=GetLocation(arg1))
                            if entryTypeID == const.refTransactionTax:
                                return localization.GetByLabel('UI/Generic/FormatReference/marketSalesTax')
                            if entryTypeID == const.refContrabandFine:
                                return localization.GetByLabel('UI/Generic/FormatReference/smugglingFine')
                            if entryTypeID == const.refManufacturing:
                                return localization.GetByLabel('UI/Generic/FormatReference/manufacturingFee', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refResearchingTechnology:
                                return localization.GetByLabel('UI/Generic/FormatReference/researchTechnologyFee', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refResearchingTimeProductivity:
                                return localization.GetByLabel('UI/Generic/FormatReference/researchTimeFee', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refResearchingMaterialProductivity:
                                return localization.GetByLabel('UI/Generic/FormatReference/researchMaterialFee', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCopying:
                                return localization.GetByLabel('UI/Generic/FormatReference/researchCopyFee', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refReverseEngineering:
                                return localization.GetByLabel('UI/Generic/FormatReference/researchInventionFee', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refContractAuctionBid:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractBid')
                            if entryTypeID == const.refContractAuctionBidRefund:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractBidRefund')
                            if entryTypeID == const.refContractCollateral:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCollateral')
                            if entryTypeID == const.refContractRewardRefund:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCollateralRewardRefund')
                            if entryTypeID == const.refContractAuctionSold:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractAuctionComplete')
                            if entryTypeID == const.refContractReward:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractComplete')
                            if entryTypeID == const.refContractCollateralRefund:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCollateralRefund')
                            if entryTypeID == const.refContractCollateralPayout:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCollateralPayout')
                            if entryTypeID == const.refContractPrice:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractAccept')
                            if entryTypeID == const.refContractBrokersFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractBrokerFee')
                            if entryTypeID == const.refContractSalesTax:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractSalesTax')
                            if entryTypeID == const.refContractDeposit:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractDeposit')
                            if entryTypeID == const.refContractDepositSalesTax:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractDepositReturnedLessTax')
                            if entryTypeID == const.refContractRewardAdded:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractRewardDepoistComplete')
                            if entryTypeID == const.refContractReversal:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractGMReversal', arg=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refContractAuctionBidCorp:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateBid', arg=arg1, name=GetName(o1))
                            if entryTypeID == const.refContractCollateralCorp:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateCollateral', arg=arg1, name=GetName(o1))
                            if entryTypeID == const.refContractPriceCorp:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateAccept', arg=arg1, name=GetName(o1))
                            if entryTypeID == const.refContractBrokersFeeCorp:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateBrokerFee', arg=arg1, name=GetName(o1))
                            if entryTypeID == const.refContractDepositCorp:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateDeposit', arg=arg1, name=GetName(o1))
                            if entryTypeID == const.refContractDepositRefund:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateDepositRefund')
                            if entryTypeID == const.refContractRewardAddedCorp:
                                return localization.GetByLabel('UI/Generic/FormatReference/contractCorporateReward', arg=arg1, name=GetName(o1))
                            if entryTypeID == const.refJumpCloneInstallationFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/cloneInstallFee')
                            if entryTypeID == const.refPaymentToLPStore:
                                return localization.GetByLabel('UI/Generic/FormatReference/lpStorePayment')
                            if entryTypeID == const.refSecureEVETimeCodeExchange:
                                return localization.GetByLabel('UI/Generic/FormatReference/plexExchangeBetween', arg=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refMedalCreation:
                                return localization.GetByLabel('UI/Generic/FormatReference/medalCreationFee', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refMedalIssuing:
                                return localization.GetByLabel('UI/Generic/FormatReference/medalIssueFee', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refAttributeRespecification:
                                return localization.GetByLabel('UI/Generic/FormatReference/attributeRemap')
                            if entryTypeID == const.refPlanetaryImportTax:
                                if arg1 is not None:
                                    planetName = cfg.evelocations.Get(arg1).name
                                else:
                                    planetName = localization.GetByLabel('UI/Generic/Unknown')
                                return localization.GetByLabel('UI/Generic/FormatReference/planetImportTax', name=GetName(o1), planet=planetName)
                            if entryTypeID == const.refPlanetaryExportTax:
                                if arg1 is not None:
                                    planetName = cfg.evelocations.Get(arg1).name
                                else:
                                    planetName = localization.GetByLabel('UI/Generic/Unknown')
                                return localization.GetByLabel('UI/Generic/FormatReference/planetExportTax', name=GetName(o1), planet=planetName)
                            if entryTypeID == const.refPlanetaryConstruction:
                                if arg1 is not None:
                                    planetName = cfg.evelocations.Get(arg1).name
                                else:
                                    planetName = localization.GetByLabel('UI/Generic/Unknown')
                                return localization.GetByLabel('UI/Generic/FormatReference/planetConstruction', name=GetName(o1), planet=planetName)
                            if entryTypeID == const.refRewardManager:
                                return localization.GetByLabel('UI/Generic/FormatReference/rewardPayout', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refStorePurchase:
                                return localization.GetByLabel('UI/Generic/FormatReference/virtualGoodsPurchase')
                            if entryTypeID == const.refStoreRefund:
                                return localization.GetByLabel('UI/Generic/FormatReference/virtualGoodsRefund')
                            if entryTypeID == const.refPlexConversion:
                                return localization.GetByLabel('UI/Generic/FormatReference/virtualGoodsPlexConversion')
                            if entryTypeID == const.refAurumGiveAway:
                                return localization.GetByLabel('UI/Generic/FormatReference/virtualGoodsLottery')
                            if entryTypeID == const.refAurumTokenConversion:
                                return localization.GetByLabel('UI/Generic/FormatReference/AurumTokenConversion')
                            if entryTypeID == const.refWarSurrenderFee:
                                return localization.GetByLabel('UI/Generic/FormatReference/WarFeeSurrender', loser=GetName(o1), winner=GetName(o2))
                            if entryTypeID == const.refWarAllyContract:
                                return localization.GetByLabel('UI/Generic/FormatReference/WarAllyContract', defender=GetName(o1), ally=GetName(o2))
                            if entryTypeID == const.refIndustryTeamEscrow:
                                return localization.GetByLabel('UI/Generic/FormatReference/industryTeamEscrow')
                            if entryTypeID == const.refIndustryTeamEscrowReimbursement:
                                return localization.GetByLabel('UI/Generic/FormatReference/industryTeamEscrowReimbursement')
                            if entryTypeID == const.refIndustryFacilityTax:
                                return localization.GetByLabel('UI/Generic/FormatReference/industryFacilityTaxRef', arg1=arg1, name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refOpportunityReward:
                                return localization.GetByLabel('UI/Generic/FormatReference/opportunityRewardDescription')
                            if entryTypeID == const.refCloneTransport:
                                return localization.GetByLabel('UI/Generic/FormatReference/cloneTransport', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCloneTransportRefund:
                                return localization.GetByLabel('UI/Generic/FormatReference/cloneTransportRefund', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refDistrictInfrastructure:
                                return localization.GetByLabel('UI/Generic/FormatReference/districtInfrastructure', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCloneSales:
                                return localization.GetByLabel('UI/Generic/FormatReference/cloneSales', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refClonePurchase:
                                return localization.GetByLabel('UI/Generic/FormatReference/clonePurchase', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refBattleRewardBiomass:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustBiomassReward', name=GetName(o1))
                            if entryTypeID == const.refBattleRewardKillSwap:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustKillSwapReward')
                            if entryTypeID == const.ACCOUNTING_DUST_CONTRACT_DEPOSIT:
                                return localization.GetByLabel('UI/Generic/FormatReference/districtContractDeposit')
                            if entryTypeID == const.ACCOUNTING_DUST_CONTRACT_DEPOSIT_REFUND:
                                return localization.GetByLabel('UI/Generic/FormatReference/districtContractDepositRefund')
                            if entryTypeID == const.ACCOUNTING_DUST_CONTRACT_COLLATERAL:
                                return localization.GetByLabel('UI/Generic/FormatReference/districtContractCollateral')
                            if entryTypeID == const.ACCOUNTING_DUST_CONTRACT_COLLATERAL_REFUND:
                                return localization.GetByLabel('UI/Generic/FormatReference/districtContractCollateralRefund')
                            if entryTypeID == const.ACCOUNTING_DUST_CONTRACT_REWARD:
                                return localization.GetByLabel('UI/Generic/FormatReference/districtContractReward')
                            if entryTypeID == const.ACCOUNTING_DUST_BATTLEREWARD_WIN:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustBattlerewardWin')
                            if entryTypeID == const.ACCOUNTING_DUST_BATTLEREWARD_LOSS:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustBattlerewardLoss')
                            if entryTypeID == const.refCP_DAILY_MISSION:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPFromDailyMission', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_WARBARGE:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPFromWarbarge', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_DONATION:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPFromDonation', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_BUY_CLONEPACKS:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPForClonePacks', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_MOVE_CLONES:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPForMovingClones', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_SELL_CLONES:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPForSellingClones', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_CHANGE_REINFORCEMENT:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPForChangingReinforcement', name1=GetName(o1), name2=GetName(o2))
                            if entryTypeID == const.refCP_CHANGE_SURFACE_INFRASTRUCTURE:
                                return localization.GetByLabel('UI/Generic/FormatReference/dustCPForChangingSurfaceInfrastructure', name1=GetName(o1), name2=GetName(o2))
                            if pretty:
                                return localization.uiutil.PrepareLocalizationSafeString('-')
                            return localization.GetByLabel('UI/Generic/FormatReference/unknowenJournalReference', ID=entryTypeID, arg=arg1, o1=o1, o2=o2)


def FmtStandingTransaction(transaction):
    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectStandingChange')
    body = ''
    try:
        if transaction.eventTypeID == logConst.eventStandingDecay:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectDecay')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageDecay')
        elif transaction.eventTypeID == logConst.eventStandingDerivedModificationPositive:
            cfg.eveowners.Prime([transaction.fromID])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectDerivedModificatonPositive')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageDerivedModificatonPositive', name=cfg.eveowners.Get(transaction.fromID).name)
        elif transaction.eventTypeID == logConst.eventStandingDerivedModificationNegative:
            cfg.eveowners.Prime([transaction.fromID])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectDerivedModificatonNegitive')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageDerivedModificatonNegitive', name=cfg.eveowners.Get(transaction.fromID).name)
        elif transaction.eventTypeID == logConst.eventStandingCombatAggression:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAgression')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAgression', locationID=transaction.int_2, ownerName=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatAssistance:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAssistence')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAssistence', locationID=transaction.int_2, name=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatShipKill:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatShipKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatShipKill', locationID=transaction.int_2, name=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingPropertyDamage:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectPropertyDamage')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messagePropertyDamage', locationID=transaction.int_2, name=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatPodKill:
            n1 = cfg.eveowners.Get(transaction.int_1).name if transaction.int_1 else '???'
            n2 = cfg.evelocations.Get(transaction.int_2).name if transaction.int_2 else '???'
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatPodKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatPodKill', locationName=n2, name=n1)
        elif transaction.eventTypeID == logConst.eventStandingSlashSet:
            n = cfg.eveowners.Get(transaction.int_1).name if transaction.int_1 else '???'
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageSetBySlashCmd', message=transaction.msg, name=n)
        elif transaction.eventTypeID == logConst.eventStandingReset:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageResetBySlashCmd')
        elif transaction.eventTypeID == logConst.eventStandingPlayerSet:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectPlayerSet')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messagePlayerSet', message=transaction.msg)
        elif transaction.eventTypeID == logConst.eventStandingPlayerCorpSet:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCorporationSet')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCorporationSet', message=transaction.msg, name=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID in (logConst.eventStandingAgentMissionCompleted,
         logConst.eventStandingAgentMissionDeclined,
         logConst.eventStandingAgentMissionFailed,
         logConst.eventStandingAgentMissionOfferExpired):
            if transaction.int_1 is not None:
                missionName = localization.GetByMessageID(transaction.int_1)
            else:
                missionName = transaction.msg
            if transaction.eventTypeID == logConst.eventStandingAgentMissionCompleted:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionComplete', message=missionName)
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionComplete', message=missionName)
            elif transaction.eventTypeID == logConst.eventStandingAgentMissionDeclined:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionDeclined', message=missionName)
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionDecline', message=missionName)
            elif transaction.eventTypeID == logConst.eventStandingAgentMissionFailed:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionFailed', message=missionName)
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionFailed', message=missionName)
            elif transaction.eventTypeID == logConst.eventStandingAgentMissionOfferExpired:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionExpired', message=missionName)
                if missionName:
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionExpiredNoMsg')
                else:
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionExpiredMsg', message=missionName)
        elif transaction.eventTypeID == logConst.eventStandingAgentMissionBonus:
            import binascii
            import cPickle
            stuff = cPickle.loads(binascii.a2b_hex(transaction.msg))
            if transaction.modification >= 0.0:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionBonus', message=stuff.get('header', '???'))
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionBonus', message=stuff.get('body', '???'))
            else:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionPenalty', message=stuff.get('header', '???'))
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionPenalty', message=stuff.get('body', '???'))
        elif transaction.eventTypeID == logConst.eventStandingPirateKillSecurityStatus:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectLawEnforcmentGain')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageLawEnforcmentGain', name=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID == logConst.eventStandingPromotionFactionIncrease:
            rankNumber = transaction.int_1
            corpID = transaction.int_2
            faction = sm.GetService('faction').GetFaction(corpID)
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarPromotion')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageFacwarPromotion', corpName=cfg.eveowners.Get(corpID).name, rankName=sm.GetService('facwar').GetRankLabel(faction, rankNumber)[0])
        elif transaction.eventTypeID == logConst.eventStandingCombatShipKillOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatShipKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatSkipKillOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatPodKillOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatPodKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatPodKillOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2)
        elif transaction.eventTypeID == logConst.eventStandingCombatAggressionOwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            typeID = transaction.int_3
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAgression')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAgressionOwnFaction', factionName=cfg.eveowners.Get(factionID).name, locationID=locationID, typeID=typeID)
        elif transaction.eventTypeID == logConst.eventStandingCombatAssistanceOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAssistence')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAssistanceOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingPropertyDamageOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectPropertyDamage')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatProprtyDamageOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingTacticalSiteDefended:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarSiteDefened')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageFacwarSiteDefened', enemyFactionName=cfg.eveowners.Get(transaction.int_2).name, factionName=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID == logConst.eventStandingTacticalSiteConquered:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarSiteConquered')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageFacwarSiteConquered', enemyFactionName=cfg.eveowners.Get(transaction.int_2).name, factionName=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID == logConst.eventStandingRecommendationLetterUsed:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectRecomendationLetterUsed')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageRecomendationLetterUsed')
        elif transaction.eventTypeID == logConst.eventStandingTutorialAgentInitial:
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageGraduation')
        elif transaction.eventTypeID == logConst.eventStandingContrabandTrafficking:
            factionID = transaction.int_1
            locationID = transaction.int_2
            if factionID:
                factionName = cfg.eveowners.Get(factionID).name
            else:
                factionName = localization.GetByLabel('UI/Generic/FormatStandingTransactions/labelSomeone')
            if locationID:
                locationName = cfg.evelocations.Get(locationID).name
            else:
                locationName = localization.GetByLabel('UI/Generic/FormatStandingTransactions/labelSomewhere')
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectContraband')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageContraband', factionName=factionName, systemName=locationName)
    except:
        log.LogException()
        sys.exc_clear()

    return (subject, body)


def FmtSystemSecStatus(raw, getColor = 0):
    sec = round(raw, 1)
    if sec == -0.0:
        sec = 0.0
    if getColor == 0:
        return sec
    else:
        if sec <= 0.0:
            colorIndex = 0
        else:
            colorIndex = int(sec * 10)
        return (sec, sm.GetService('map').GetSecColorList()[colorIndex])


def GetStandingEventTypes():
    return [(localization.GetByLabel('UI/Generic/StandingNames/agentByoff'), logConst.eventStandingAgentBuyOff),
     (localization.GetByLabel('UI/Generic/StandingNames/agentDonation'), logConst.eventStandingAgentDonation),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionBonus'), logConst.eventStandingAgentMissionBonus),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionComplete'), logConst.eventStandingAgentMissionCompleted),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionDeclined'), logConst.eventStandingAgentMissionDeclined),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionFailed'), logConst.eventStandingAgentMissionFailed),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionExpired'), logConst.eventStandingAgentMissionOfferExpired),
     (localization.GetByLabel('UI/Generic/StandingNames/combatAgression'), logConst.eventStandingCombatAggression),
     (localization.GetByLabel('UI/Generic/StandingNames/combatOther'), logConst.eventStandingCombatOther),
     (localization.GetByLabel('UI/Generic/StandingNames/combatPodKill'), logConst.eventStandingCombatPodKill),
     (localization.GetByLabel('UI/Generic/StandingNames/combatShipKill'), logConst.eventStandingCombatShipKill),
     (localization.GetByLabel('UI/Generic/StandingNames/decay'), logConst.eventStandingDecay),
     (localization.GetByLabel('UI/Generic/StandingNames/derivedNegitive'), logConst.eventStandingDerivedModificationNegative),
     (localization.GetByLabel('UI/Generic/StandingNames/derivedPositive'), logConst.eventStandingDerivedModificationPositive),
     (localization.GetByLabel('UI/Generic/StandingNames/agentInital'), logConst.eventStandingInitialCorpAgent),
     (localization.GetByLabel('UI/Generic/StandingNames/factionInital'), logConst.eventStandingInitialFactionAlly),
     (localization.GetByLabel('UI/Generic/StandingNames/factionInitalCorp'), logConst.eventStandingInitialFactionCorp),
     (localization.GetByLabel('UI/Generic/StandingNames/factionInitalEnemy'), logConst.eventStandingInitialFactionEnemy),
     (localization.GetByLabel('UI/Generic/StandingNames/lawEnforcement'), logConst.eventStandingPirateKillSecurityStatus),
     (localization.GetByLabel('UI/Generic/StandingNames/playerCorpSetStandings'), logConst.eventStandingPlayerCorpSet),
     (localization.GetByLabel('UI/Generic/StandingNames/playerSetStandings'), logConst.eventStandingPlayerSet),
     (localization.GetByLabel('UI/Generic/StandingNames/entityRecacluate'), logConst.eventStandingRecalcEntityKills),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionRecaculateFailed'), logConst.eventStandingRecalcMissionFailure),
     (localization.GetByLabel('UI/Generic/StandingNames/agentMissionRecaculateSucess'), logConst.eventStandingRecalcMissionSuccess),
     (localization.GetByLabel('UI/Generic/StandingNames/entityRecaculatePirateKills'), logConst.eventStandingRecalcPirateKills),
     (localization.GetByLabel('UI/Generic/StandingNames/playerRecaculateSetStandings'), logConst.eventStandingRecalcPlayerSet),
     (localization.GetByLabel('UI/Generic/StandingNames/GMSlashSet'), logConst.eventStandingSlashSet),
     (localization.GetByLabel('UI/Generic/StandingNames/standingReset'), logConst.eventStandingReset),
     (localization.GetByLabel('UI/Generic/StandingNames/tutorialInitial'), logConst.eventStandingTutorialAgentInitial),
     (localization.GetByLabel('UI/Generic/StandingNames/standingsUpdate'), logConst.eventStandingUpdate)]


def GetName(ownerID):
    try:
        if ownerID == -1:
            return '(none)'
        if ownerID < 0:
            return evetypes.GetName(-ownerID)
        return cfg.eveowners.Get(ownerID).name
    except:
        sys.exc_clear()
        return localization.uiutil.PrepareLocalizationSafeString('id:%s (no name)' % ownerID)


def GetLocation(locationID):
    try:
        if boot.role == 'server' or eve.session.regionid < const.mapWormholeRegionMin:
            return cfg.evelocations.Get(locationID).name
        if locationID >= const.mapWormholeRegionMin and locationID <= const.mapWormholeRegionMax:
            return localization.GetByLabel('UI/Generic/FormatLocations/unchartedRegion')
        if locationID >= const.mapWormholeConstellationMin and locationID <= const.mapWormholeConstellationMax:
            return localization.GetByLabel('UI/Generic/FormatLocations/unchartedConstellation')
        if locationID >= const.mapWormholeSystemMin and locationID <= const.mapWormholeSystemMax:
            return localization.GetByLabel('UI/Generic/FormatLocations/unchartedSystem')
    except:
        sys.exc_clear()
        return localization.GetByLabel('UI/Generic/FormatLocations/errorUnknowenLocation', id=locationID)


def FmtProbeState(state, colorize = False):
    stateText = localization.GetByLabel(PROBE_STATE_TEXT_MAP[state])
    if colorize:
        return PROBE_STATE_COLOR_MAP[state] % stateText
    else:
        return stateText


def FmtPlanetAttributeKeyVal(key, val):
    text = val
    label = None
    if key == 'temperature':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeTemperature')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatTempatureKelvin', value=str(int(val)))
    elif key == 'orbitRadius':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeOrbitRadius')
        numAU = val / const.AU
        if numAU > 0.1:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalRadiusInAU', value=numAU)
        else:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalRadiusInKM', value=FmtAmt(int(val)))
    elif key == 'eccentricity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeEccentricity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatEccentricity', value=val)
    elif key == 'massDust':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeMassDust')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatMassInKG', value='%.1e' % val)
    elif key == 'massGas':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeMassGas')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatMassInKG', value='%.1e' % val)
    elif key == 'density':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeDensity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatDensity', value=val)
    elif key == 'orbitPeriod':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeOrbitPeriod')
        numDays = val / 864000
        if numDays > 1.0:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalPeriodInt', value=int(numDays))
        else:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalPeriodFloat', value=numDays)
    elif key in ('age',):
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeAge')
        value = int(val / 31536000 / 1000000) * 1000000
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatAge', value=value)
    elif key == 'radius':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeRadius')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalRadiusInKM', value=FmtAmt(int(val / 1000)))
    elif key == 'surfaceGravity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeSurfaceGravity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatSurfaceGravity', value=val)
    elif key == 'escapeVelocity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeEscapeVelocity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatEscapeVelocity', value=val / 1000)
    elif key == 'pressure':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributePressure')
        if val < 1000:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatSurfacePresureVeryLow')
        else:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatSurfacePresure', value=val / 100000)
    elif key == 'fragmented':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeFragmented')
    elif key == 'life':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeLife')
    elif key == 'locked':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeLocked')
    elif key == 'luminosity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeLuminosity')
        text = localization.formatters.FormatNumeric(text)
    elif key == 'mass':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeMass')
    elif key == 'rotatopmRate':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeRotatopmRate')
    elif key == 'spectralClass':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeSpectralClass')
    return (label, text)


def FmtDist2(dist, maxDecimals = 2):
    if dist < 0.0:
        dist = abs(dist)
        maxDecimals = None
    if dist < 10000.0:
        dist = int(dist)
        maxDecimals = None
        fmtUrl = '/Carbon/UI/Common/FormatDistance/fmtDistInMeters'
    elif dist < 10000000000.0:
        dist = float(dist) / 1000.0
        fmtUrl = '/Carbon/UI/Common/FormatDistance/fmtDistInKiloMeters'
    else:
        dist = round(dist / const.AU, maxDecimals)
        fmtUrl = '/Carbon/UI/Common/FormatDistance/fmtDistInAU'
    if maxDecimals == 0:
        maxDecimals = None
        dist = int(dist)
    distStr = localization.formatters.FormatNumeric(dist, useGrouping=False, decimalPlaces=maxDecimals)
    return localization.GetByLabel(fmtUrl, distance=distStr)


def FmtISKEng(isk, showFractionsAlways = 1):
    return FmtCurrencyEng(isk, showFractionsAlways, const.creditsISK)


def FmtAUREng(aur, showFractionsAlways = 0):
    return FmtCurrencyEng(aur, showFractionsAlways, const.creditsAURUM)


def FmtCurrencyEng(amount, showFractionsAlways = 1, currency = None):
    if currency == const.creditsAURUM:
        currencyString = ' AUR'
    elif currency == const.creditsISK:
        currencyString = ' ISK'
    else:
        currencyString = ''
    minus = ['-', ''][amount >= 0]
    fractions = 0.0
    try:
        fractions = abs(math.fmod(amount, 1.0))
        if amount is None:
            amount = 0
        amount = long(amount)
    except:
        log.LogTraceback()
        raise RuntimeError('Value must be Int, Long or Float')

    ret = ''
    digit = ''
    amt = str(abs(amount))
    for i in xrange(len(amt) % 3, len(amt) + 3, 3):
        if i < 3:
            ret += amt[:i]
        else:
            ret += digit + amt[i - 3:i]
        if i != 0:
            digit = [',', '.'][DECIMAL == ',']

    if fractions != 0.0 and currency != const.creditsAURUM or showFractionsAlways:
        if round(fractions * 100) / 100 == 1:
            return FmtAmt(float('%s%s' % (minus, ret.replace(digit, ''))) + 1, showFraction=showFractionsAlways * 2) + currencyString
        rest = str(100 * round(fractions, 2))[:2]
        if rest[1] == '.':
            rest = '0' + rest[0]
        ret = '%s%s%s' % (ret, DECIMAL, rest)
    return minus + ret + currencyString


def GetAveragePrice(item):
    if item.singleton == const.singletonBlueprintCopy:
        return
    try:
        import inventorycommon.typeHelpers
        return inventorycommon.typeHelpers.GetAveragePrice(item.typeID)
    except KeyError:
        return


def FmtOwnerLink(ownerID):
    owner = cfg.eveowners.Get(ownerID)
    return '<url=showinfo:%d//%d>%s</url>' % (owner.typeID, owner.ownerID, owner.ownerName)


exports = {'util.FmtISK': FmtISK,
 'util.FmtISKAndRound': FmtISKAndRound,
 'util.RoundISK': RoundISK,
 'util.FmtAUR': FmtAUR,
 'util.FmtCurrency': FmtCurrency,
 'util.FmtRef': FmtRef,
 'util.FmtStandingTransaction': FmtStandingTransaction,
 'util.GetStandingEventTypes': GetStandingEventTypes,
 'util.FmtSystemSecStatus': FmtSystemSecStatus,
 'util.FmtProbeState': FmtProbeState,
 'util.GetLocation': GetLocation,
 'util.FmtPlanetAttributeKeyVal': FmtPlanetAttributeKeyVal,
 'util.FmtDist2': FmtDist2,
 'util.FmtISKEng': FmtISKEng,
 'util.FmtAUREng': FmtAUREng,
 'util.FmtCurrencyEng': FmtCurrencyEng,
 'util.GetAveragePrice': GetAveragePrice,
 'util.FmtOwnerLink': FmtOwnerLink}
