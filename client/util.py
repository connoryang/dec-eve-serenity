#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\util.py
from crimewatch.util import GetKillReportHashValue
from datetimeutils import FromBlueTime
from utillib import KeyVal
from carbon.common.lib.whitelist import InitWhitelist
from carbon.common.script.net.cachedObject import CachedObject
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.net.moniker import UpdateMoniker
from carbon.common.script.net.moniker import allMonikers
from carbon.common.script.sys.cfg import Config as config
from carbon.common.script.sys.row import Row
from carbon.common.script.util.blue2Py import WrapBlueClass as Blue2Py
from carbon.common.script.util.blue2Py import TestCopyTo
from carbon.common.script.util.blue2Py import TestPersistance
from carbon.common.script.util.blueNotifyWrapper import BlueClassNotifyWrap
from carbon.common.script.util.callback import Callback
from carbon.common.script.util.commonutils import Clamp
from carbon.common.script.util.commonutils import GetAttrs
from carbon.common.script.util.commonutils import HasDialogueHyperlink
from carbon.common.script.util.commonutils import IsFullLogging
from carbon.common.script.util.commonutils import Object
from carbon.common.script.util.commonutils import Truncate
from carbon.common.script.util.componentCommon import UnpackStringToTuple
from carbon.common.script.util.datatable import DataTable
from carbon.common.script.util.datatable import DataTableException
from carbon.common.script.util.datatable import DataTableQuery
from carbon.common.script.util.exceptionEater import ExceptionEater
from carbon.common.script.util.format import BlueToDate
from carbon.common.script.util.format import CaseFold
from carbon.common.script.util.format import CaseFoldCompare
from carbon.common.script.util.format import CaseFoldEquals
from carbon.common.script.util.format import ConvertDate
from carbon.common.script.util.format import DateToBlue
from carbon.common.script.util.format import DECIMAL
from carbon.common.script.util.format import DIGIT
from carbon.common.script.util.format import EscapeAdHocSQL
from carbon.common.script.util.format import EscapeSQL
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.format import FmtAmtEng
from carbon.common.script.util.format import FmtCdkey
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.format import FmtDateEng
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.format import FmtSec
from carbon.common.script.util.format import FmtSecEng
from carbon.common.script.util.format import FmtSimpleDateUTC
from carbon.common.script.util.format import FmtTime
from carbon.common.script.util.format import FmtTimeEng
from carbon.common.script.util.format import FmtTimeInterval
from carbon.common.script.util.format import FmtTimeIntervalEng
from carbon.common.script.util.format import FmtVec
from carbon.common.script.util.format import FormatTimeAgo
from carbon.common.script.util.format import FormatUrl
from carbon.common.script.util.format import GetKeyAndNormalize
from carbon.common.script.util.format import GetTimeParts
from carbon.common.script.util.format import GetYearMonthFromTime
from carbon.common.script.util.format import IntToRoman
from carbon.common.script.util.format import LFromUI
from carbon.common.script.util.format import LineWrap
from carbon.common.script.util.format import ParseDate
from carbon.common.script.util.format import ParseDateTime
from carbon.common.script.util.format import ParseSmallDate
from carbon.common.script.util.format import ParseTime
from carbon.common.script.util.format import ParseTimeInterval
from carbon.common.script.util.format import PasswordString
from carbon.common.script.util.format import RomanToInt
from carbon.common.script.util.format import StrFromColor
from carbon.common.script.util.format import dateConvert
from carbon.common.script.util.funcDeco import ClearMemoized
from carbon.common.script.util.funcDeco import Memoized
from carbon.common.script.util.guidUtils import MakeGUID
from carbon.common.script.util.guidUtils import MakePUID
from carbon.common.script.util.inspect import IsClassMethod
from carbon.common.script.util.inspect import IsNormalMethod
from carbon.common.script.util.inspect import IsStaticMethod
from carbon.common.script.util.memoize import Memoize
from carbon.common.script.util.rateLimitedQueue import RateLimitedQueue
from carbon.common.script.util.simpleEval import SimpleEval
from carbon.common.script.util.stringManip import Decode
from carbon.common.script.util.stringManip import Encode
from carbon.common.script.util.stringManip import TruncateStringTo
from carbon.common.script.util.timerstuff import Stopwatch
from carbon.common.script.util.traceref import ClassOrType
from carbon.common.script.util.traceref import GetLiveObjectsByType
from carbon.common.script.util.traceref import GetLiveObjectsByTypeName
from carbon.common.script.util.traceref import ObjectHistogram
from carbon.common.script.util.traceref import PrintRefPaths
from carbon.common.script.util.traceref import TestAnnotatedRefGraph
from carbon.common.script.util.traceref import TestRawRefGraph
from carbon.common.script.util.typeConversion import CastValue
from carbon.common.script.util.weight import ChooseWeighted as weightedChoice
from carbon.common.script.util.wrapper import Wrapper
from carbon.common.script.util.xpermutations import xcombinations
from carbon.common.script.util.xpermutations import xpermutations
from carbon.common.script.util.xpermutations import xselections
from carbon.common.script.util.xpermutations import xuniqueCombinations
from carbon.client.script.graphics.isLoaded import IsAreaLoading
from carbon.client.script.graphics.isLoaded import IsTr2EffectLoading
from carbon.client.script.graphics.isLoaded import IsTr2MeshLoading
from carbon.client.script.graphics.isLoaded import IsTr2ModelLoading
from carbon.client.script.graphics.isLoaded import IsTr2SkinnedModelLoading
from carbonui.util.color import Color
from carbon.common.script.util.mathCommon import ConvertGeoToTriMatrix
from carbon.common.script.util.mathCommon import ConvertTriToGeoMatrix
from carbon.common.script.util.mathCommon import ConvertTriToTupleMatrix
from carbon.common.script.util.mathCommon import ConvertTupleToTriMatrix
from carbon.client.script.util.misc import BlueFile
from carbon.client.script.util.misc import Clamp
from carbon.client.script.util.misc import Decorator
from carbon.client.script.util.misc import DelTree
from carbon.client.script.util.misc import Despammer
from carbon.client.script.util.misc import Doppleganger
from carbon.client.script.util.misc import GetAttrs
from carbon.client.script.util.misc import HasAttrs
from carbon.client.script.util.misc import HoursMinsSecsFromSecs
from carbon.client.script.util.misc import ResFile
from carbon.client.script.util.misc import ResFileToCache
from carbon.client.script.util.misc import RunOnceMethod
from carbon.client.script.util.misc import SecsFromBlueTimeDelta
from carbon.client.script.util.misc import TryDel
from carbon.client.script.util.misc import Uthreaded
from carbon.client.script.util.resLoader import ResFile
from carbon.client.script.util.weakrefutil import CallableWeakRef
from carbon.client.script.util.weakrefutil import WeakRefAttrObject
from eve.common.script.sys.dbrow import ConstValueExists
from eve.common.script.sys.dbrow import LookupConstValue
from eve.common.script.sys.devIndexUtil import GetDevIndexLevels
from eve.common.script.sys.devIndexUtil import GetTimeIndexLevelForDays
from eve.common.script.sys.devIndexUtil import GetTimeIndexLevels
from eve.common.script.sys.devIndexUtil import devIndexDecayRate
from eve.common.script.sys.devIndexUtil import timeIndexLevels
from eve.common.script.sys.eveCfg import CanUseAgent
from eve.common.script.sys.eveCfg import DgmAttribute
from eve.common.script.sys.eveCfg import DgmEffect
from eve.common.script.sys.eveCfg import DgmUnit
from eve.common.script.sys.eveCfg import EveConfig
from eve.common.script.sys.eveCfg import GetActiveShip
from eve.common.script.sys.eveCfg import GetCharacterType
from eve.common.script.sys.eveCfg import GetPlanetWarpInPoint
from eve.common.script.sys.eveCfg import GetReprocessingOptions
from eve.common.script.sys.eveCfg import GetShipFlagLocationName
from eve.common.script.sys.eveCfg import GraphicFile
from eve.common.script.sys.eveCfg import IconFile
from eve.common.script.sys.eveCfg import IsAlliance
from eve.common.script.sys.eveCfg import IsAllyActive
from eve.common.script.sys.eveCfg import IsAtWar
from eve.common.script.sys.eveCfg import IsBookmarkModerator
from eve.common.script.sys.eveCfg import IsCelestial
from eve.common.script.sys.eveCfg import IsCharacter
from eve.common.script.sys.eveCfg import IsConstellation
from eve.common.script.sys.eveCfg import IsControlBunker
from eve.common.script.sys.eveCfg import IsCorporation
from eve.common.script.sys.eveCfg import IsDistrict
from eve.common.script.sys.eveCfg import IsDustCharacter
from eve.common.script.sys.eveCfg import IsDustType
from eve.common.script.sys.eveCfg import IsDustUser
from eve.common.script.sys.eveCfg import IsEvePlayerCharacter
from eve.common.script.sys.eveCfg import IsEveUser
from eve.common.script.sys.eveCfg import IsFaction
from eve.common.script.sys.eveCfg import IsFactoryFolder
from eve.common.script.sys.eveCfg import IsFakeItem
from eve.common.script.sys.eveCfg import IsFlagSubSystem
from eve.common.script.sys.eveCfg import IsJunkLocation
from inventorycommon.util import IsNPC
from eve.common.script.sys.eveCfg import IsNPCCharacter
from eve.common.script.sys.eveCfg import IsNPCCorporation
from eve.common.script.sys.eveCfg import IsNewbieSystem
from eve.common.script.sys.eveCfg import IsOfficeFolder
from eve.common.script.sys.eveCfg import IsOrbital
from eve.common.script.sys.eveCfg import IsOutlawStatus
from eve.common.script.sys.eveCfg import IsOutpost
from eve.common.script.sys.eveCfg import IsOwner
from eve.common.script.sys.eveCfg import IsPlaceable
from eve.common.script.sys.eveCfg import IsPlayerAvatar
from eve.common.script.sys.eveCfg import IsPlayerItem
from eve.common.script.sys.eveCfg import IsPlayerOwner
from eve.common.script.sys.eveCfg import IsPolarisFrigate
from eve.common.script.sys.eveCfg import IsPreviewable
from eve.common.script.sys.eveCfg import IsRegion
from eve.common.script.sys.eveCfg import IsSolarSystem
from eve.common.script.sys.eveCfg import IsStargate
from eve.common.script.sys.eveCfg import IsStation
from eve.common.script.sys.eveCfg import IsStarbase
from eve.common.script.sys.eveCfg import IsSystem
from eve.common.script.sys.eveCfg import IsSystemOrNPC
from eve.common.script.sys.eveCfg import IsTrading
from eve.common.script.sys.eveCfg import IsUniverseAsteroid
from eve.common.script.sys.eveCfg import IsUniverseCelestial
from eve.common.script.sys.eveCfg import IsWarActive
from eve.common.script.sys.eveCfg import IsWarInHostileState
from eve.common.script.sys.eveCfg import IsWorldSpace
from inventorycommon.util import IsWormholeConstellation
from inventorycommon.util import IsWormholeRegion
from inventorycommon.util import IsWormholeSystem
from eve.common.script.sys.eveCfg import MakeConstantName
from eve.common.script.sys.eveCfg import RamActivityVirtualColumn
from eve.common.script.sys.eveCfg import Singleton
from eve.common.script.sys.eveCfg import StackSize
from eve.common.script.sys.eveCfg import BULKDEFINITIONS as bulkDataTableDefinitions
from eve.common.script.sys.eveCfg import BULKVERSION as bulkDataVersion
from eve.common.script.sys.rowset import FilterRowset
from eve.common.script.sys.rowset import IndexRowset
from eve.common.script.sys.rowset import IndexedRowLists
from eve.common.script.sys.rowset import IndexedRows
from eve.common.script.sys.rowset import Rowset
from eve.common.script.sys.rowset import SparseRowset
from eve.common.script.sys.rowset import SparseRowsetProvider
from eve.common.script.util.eveCommonUtils import AUPerSecondToDestinyWarpSpeed
from eve.common.script.util.eveCommonUtils import CombatLog_CopyText
from eve.common.script.util.eveCommonUtils import GetPublicCrestUrl
from eve.common.script.util.eveCommonUtils import Flatten
from dogma.effects import GetEwarTypeByEffectID
from eve.common.script.util.eveCommonUtils import GetKillMailInfo
from eve.common.script.util.eveCommonUtils import IsDustEnabled
from eve.common.script.util.eveCommonUtils import IsMemberlessLocal
from eve.common.script.util.eveCommonUtils import SecurityClassFromLevel
from eve.common.script.util.eveFormat import FmtAUR
from eve.common.script.util.eveFormat import FmtAUREng
from eve.common.script.util.eveFormat import FmtCurrency
from eve.common.script.util.eveFormat import FmtCurrencyEng
from eve.common.script.util.eveFormat import FmtDist2
from eve.common.script.util.eveFormat import FmtISK
from eve.common.script.util.eveFormat import FmtISKAndRound
from eve.common.script.util.eveFormat import FmtISKEng
from eve.common.script.util.eveFormat import FmtOwnerLink
from eve.common.script.util.eveFormat import FmtPlanetAttributeKeyVal
from eve.common.script.util.eveFormat import FmtProbeState
from eve.common.script.util.eveFormat import FmtRef
from eve.common.script.util.eveFormat import FmtStandingTransaction
from eve.common.script.util.eveFormat import FmtSystemSecStatus
from eve.common.script.util.eveFormat import GetAveragePrice
from eve.common.script.util.eveFormat import GetLocation
from eve.common.script.util.eveFormat import GetStandingEventTypes
from eve.common.script.util.eveFormat import RoundISK
from eve.common.script.util.pagedCollection import PagedCollection
from eve.common.script.util.pagedCollection import PagedResultSet
from eve.client.script.environment.spaceObject.ExplosionManager import ExplosionManager
from eve.client.script.environment.spaceObject.ExplosionManager import GetLodLevel
from eve.client.script.parklife.state import CRIMINAL_RED
from eve.client.script.parklife.state import GetNPCGroups
from eve.client.script.parklife.state import NORELATIONSHIP_SENTINEL
from eve.client.script.parklife.state import STATE_COLORS
from eve.client.script.parklife.state import SUSPECT_YELLOW
from eve.client.script.parklife.state import StateProperty
from eve.client.script.parklife.state import TURQUOISE
from eve.client.script.ui.camera.baseCamera import Camera
from eve.client.script.ui.login.antiaddiction import Time
from eve.client.script.ui.shared.killReportUtil import CleanKillMail
from eve.client.script.util.bubble import InBubble
from eve.client.script.util.bubble import SlimItemFromCharID
from eve.client.script.util.eveMisc import CSPAChargedAction
from eve.client.script.util.eveMisc import IsItemOfRepairableType
from eve.client.script.util.eveMisc import LaunchFromShip
