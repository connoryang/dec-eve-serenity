#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatting\notificationFormatMapping.py
import eve.common.script.util.notificationconst as notificationConst
from notifications.common.formatters.achievementTask import AchievementTaskFormatter
from notifications.common.formatters.contactFormatters import ContactAddFormatter, ContactEditFormatter, BuddyContactAddFormatter
from notifications.common.formatters.contractAssigned import ContractAssignedFormatter
from notifications.common.formatters.contractAttention import ContractNeedsAttentionFormatter
from notifications.common.formatters.killMailFinalBlow import KillMailFinalBlowFormatter
from notifications.common.formatters.killMailVictim import KillMailVictimFormatter
from notifications.common.formatters.mailsummary import MailSummaryFormatter
from notifications.common.formatters.newMail import NewMailFormatter
from notifications.common.formatters.opportunity import AchievementOpportunityFormatter
from notifications.common.formatters.plexDonation import PlexDonationReceivedFormatter, PlexDonationSentFormatter
from notifications.common.formatters.skillPoints import UnusedSkillPointsFormatter
from notifications.common.formatters.sovAllianceCapitalChange import SovAllianceCapitalChanged
from notifications.common.formatters.sovBase import SovStructureDestroyed, SovEntosisCaptureStarted, SovStationServiceEnabled, SovStationServiceDisabled, SovStationServiceHalfCaptured, SovStructureDestructFinished
from notifications.common.formatters.sovBase import SovIHubDestroyedByBillFailure
from notifications.common.formatters.sovCommandNodeEvent import SovCommandNodeEventStarted
from notifications.common.formatters.sovIHubBillAboutToExpire import IHubBillAboutToExpire
from notifications.common.formatters.sovStationEnteredFreeport import SovStationEnteredFreeport
from notifications.common.formatters.sovStructureReinforced import SovStructureReinforced
from notifications.common.formatters.structureDestructCancel import StructureDestructCancel
from notifications.common.formatters.structureDestructRequested import StructureDestructRequested

class NotificationFormatMapper:

    def __init__(self):
        self.registry = {notificationConst.notificationTypeMailSummary: MailSummaryFormatter,
         notificationConst.notificationTypeNewMailFrom: NewMailFormatter,
         notificationConst.notificationTypeUnusedSkillPoints: UnusedSkillPointsFormatter,
         notificationConst.notificationTypeContractNeedsAttention: ContractNeedsAttentionFormatter,
         notificationConst.notificationTypeContractAssigned: ContractAssignedFormatter,
         notificationConst.notificationTypeKillReportVictim: KillMailVictimFormatter,
         notificationConst.notificationTypeKillReportFinalBlow: KillMailFinalBlowFormatter,
         notificationConst.notificationTypeAchievementTaskFinished: AchievementTaskFormatter,
         notificationConst.notificationTypeOpportunityFinished: AchievementOpportunityFormatter,
         notificationConst.notificationTypeGameTimeReceived: PlexDonationReceivedFormatter,
         notificationConst.notificationTypeGameTimeSent: PlexDonationSentFormatter,
         notificationConst.notificationTypeEntosisCaptureStarted: SovEntosisCaptureStarted,
         notificationConst.notificationTypeStationServiceEnabled: SovStationServiceEnabled,
         notificationConst.notificationTypeStationServiceDisabled: SovStationServiceDisabled,
         notificationConst.notificationTypeStationServiceHalfCaptured: SovStationServiceHalfCaptured,
         notificationConst.notificationTypeSovStructureDestroyed: SovStructureDestroyed,
         notificationConst.notificationTypeSovStructureSelfDestructRequested: StructureDestructRequested,
         notificationConst.notificationTypeSovStructureSelfDestructCancel: StructureDestructCancel,
         notificationConst.notificationTypeSovStructureSelfDestructFinished: SovStructureDestructFinished,
         notificationConst.notificationTypeIHubDestroyedByBillFailure: SovIHubDestroyedByBillFailure,
         notificationConst.notificationTypeSovStationEnteredFreeport: SovStationEnteredFreeport,
         notificationConst.notificationTypeAllianceCapitalChanged: SovAllianceCapitalChanged,
         notificationConst.notificationTypeSovCommandNodeEventStarted: SovCommandNodeEventStarted,
         notificationConst.notificationTypeSovStructureReinforced: SovStructureReinforced,
         notificationConst.notificationTypeInfrastructureHubBillAboutToExpire: IHubBillAboutToExpire,
         notificationConst.notificationTypeContactAdd: ContactAddFormatter,
         notificationConst.notificationTypeContactEdit: ContactEditFormatter,
         notificationConst.notificationTypeBuddyConnectContactAdd: BuddyContactAddFormatter}

    def Register(self, notificationTypeID, formatter):
        self.registry[notificationTypeID] = formatter

    def GetFormatterForType(self, typeID):
        if typeID in self.registry:
            return self.registry[typeID]()
        else:
            return None
