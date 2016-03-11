#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\mapcommon.py
from eve.client.script.ui.shared.maps.mapcommon import ACTUAL_COLOR_OVERGLOWFACTOR
from eve.client.script.ui.shared.maps.mapcommon import COLORCURVE_SECURITY
from eve.client.script.ui.shared.maps.mapcommon import COLORMODE_CONSTELLATION
from eve.client.script.ui.shared.maps.mapcommon import COLORMODE_FACTION
from eve.client.script.ui.shared.maps.mapcommon import COLORMODE_POPULATION
from eve.client.script.ui.shared.maps.mapcommon import COLORMODE_REGION
from eve.client.script.ui.shared.maps.mapcommon import COLORMODE_STANDINGS
from eve.client.script.ui.shared.maps.mapcommon import COLORMODE_UNIFORM
from eve.client.script.ui.shared.maps.mapcommon import COLOR_CONSTELLATION
from eve.client.script.ui.shared.maps.mapcommon import COLOR_REGION
from eve.client.script.ui.shared.maps.mapcommon import COLOR_SOLARSYSTEM
from eve.client.script.ui.shared.maps.mapcommon import COLOR_STANDINGS_BAD
from eve.client.script.ui.shared.maps.mapcommon import COLOR_STANDINGS_GOOD
from eve.client.script.ui.shared.maps.mapcommon import COLOR_STANDINGS_NEUTRAL
from eve.client.script.ui.shared.maps.mapcommon import CONSTELLATION_JUMP
from eve.client.script.ui.shared.maps.mapcommon import DISPLAYMODE_ALL
from eve.client.script.ui.shared.maps.mapcommon import DISPLAYMODE_NEIGHBORS
from eve.client.script.ui.shared.maps.mapcommon import DISPLAYMODE_NEIGHBORS2X
from eve.client.script.ui.shared.maps.mapcommon import DISPLAYMODE_SINGLE
from eve.client.script.ui.shared.maps.mapcommon import JUMPBRIDGE_ANIMATION_SPEED
from eve.client.script.ui.shared.maps.mapcommon import JUMPBRIDGE_COLOR
from eve.client.script.ui.shared.maps.mapcommon import JUMPBRIDGE_COLOR_SCALE
from eve.client.script.ui.shared.maps.mapcommon import JUMPBRIDGE_CURVE_SCALE
from eve.client.script.ui.shared.maps.mapcommon import JUMP_COLORS
from eve.client.script.ui.shared.maps.mapcommon import JUMP_TYPES
from eve.client.script.ui.shared.maps.mapcommon import LINESET_3D_EFFECT_STARMAP
from eve.client.script.ui.shared.maps.mapcommon import LINESET_EFFECT
from eve.client.script.ui.shared.maps.mapcommon import LINESET_EFFECT_STARMAP
from eve.client.script.ui.shared.maps.mapcommon import LegendItem
from eve.client.script.ui.shared.maps.mapcommon import MODE_CONSTELLATION
from eve.client.script.ui.shared.maps.mapcommon import MODE_HIDE
from eve.client.script.ui.shared.maps.mapcommon import MODE_NOLINES
from eve.client.script.ui.shared.maps.mapcommon import MODE_REGION
from eve.client.script.ui.shared.maps.mapcommon import MODE_SOLARSYSTEM
from eve.client.script.ui.shared.maps.mapcommon import MODE_UNIVERSE
from eve.client.script.ui.shared.maps.mapcommon import NEUTRAL_COLOR
from eve.client.script.ui.shared.maps.mapcommon import REGION_JUMP
from eve.client.script.ui.shared.maps.mapcommon import SOLARSYSTEM_JUMP
from eve.client.script.ui.shared.maps.mapcommon import SOV_CHANGES_ALL
from eve.client.script.ui.shared.maps.mapcommon import SOV_CHANGES_OUTPOST_CONQUERED
from eve.client.script.ui.shared.maps.mapcommon import SOV_CHANGES_OUTPOST_GAIN
from eve.client.script.ui.shared.maps.mapcommon import SOV_CHANGES_OUTPOST_LOST
from eve.client.script.ui.shared.maps.mapcommon import SOV_CHANGES_SOV_GAIN
from eve.client.script.ui.shared.maps.mapcommon import SOV_CHANGES_SOV_LOST
from eve.client.script.ui.shared.maps.mapcommon import STARMAP_SCALE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_ASSETS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_AVOIDANCE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_BOOKMARKED
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CARGOILLEGALITY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CONSTSOVEREIGNTY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CORPDELIVERIES
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CORPIMPOUNDED
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CORPOFFICES
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CORPPROPERTY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_CYNOSURALFIELDS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_DUNGEONS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_DUNGEONSAGENTS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FACTION
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FACTIONEMPIRE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FACTIONKILLS1HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FILTER_EMPIRE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FILTER_FACWAR_ENEMY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FILTER_FACWAR_MINE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FRIENDS_AGENT
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FRIENDS_CONTACTS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FRIENDS_CORP
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FRIENDS_FLEET
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_INCURSION
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_INCURSIONGM
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_INDEX_INDUSTRY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_INDEX_MILITARY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_INDEX_STRATEGIC
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_JUMPS1HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_MILITIA
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_MILITIAKILLS1HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_MILITIAKILLS24HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_MYCOLONIES
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_OUTPOST_GAIN
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_OUTPOST_LOSS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_PISCANRANGE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_PLANETTYPE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_PLAYERCOUNT
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_PLAYERDOCKED
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_PODKILLS1HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_PODKILLS24HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_REAL
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_REGION
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SECURITY
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_AssassinationMissions
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_BlackMarket
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Cloning
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_CourierMissions
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_DNATherapy
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Factory
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Fitting
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Gambling
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Insurance
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Interbus
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Laboratory
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Market
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_NavyOffices
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_News
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Paintshop
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Refinery
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_RepairFacilities
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_ReprocessingPlant
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_SecurityOffice
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_StockExchange
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Storage
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_Surgery
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SHIPKILLS1HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SHIPKILLS24HR
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SOV_CHANGE
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SOV_GAIN
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SOV_LOSS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SOV_STANDINGS
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_STATIONCOUNT
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_VISITED
from eve.client.script.ui.shared.maps.mapcommon import SUN_BLUE
from eve.client.script.ui.shared.maps.mapcommon import SUN_BLUE_BRIGHT
from eve.client.script.ui.shared.maps.mapcommon import SUN_DATA
from eve.client.script.ui.shared.maps.mapcommon import SUN_ORANGE
from eve.client.script.ui.shared.maps.mapcommon import SUN_ORANGE_BRIGHT
from eve.client.script.ui.shared.maps.mapcommon import SUN_PINK
from eve.client.script.ui.shared.maps.mapcommon import SUN_RED
from eve.client.script.ui.shared.maps.mapcommon import SUN_SIZE_DWARF
from eve.client.script.ui.shared.maps.mapcommon import SUN_SIZE_GIANT
from eve.client.script.ui.shared.maps.mapcommon import SUN_SIZE_LARGE
from eve.client.script.ui.shared.maps.mapcommon import SUN_SIZE_MEDIUM
from eve.client.script.ui.shared.maps.mapcommon import SUN_SIZE_SMALL
from eve.client.script.ui.shared.maps.mapcommon import SUN_WHITE
from eve.client.script.ui.shared.maps.mapcommon import SUN_YELLOW
from eve.client.script.ui.shared.maps.mapcommon import SYSTEMMAP_SCALE
from eve.client.script.ui.shared.maps.mapcommon import TILE_MODE_SOVEREIGNTY
from eve.client.script.ui.shared.maps.mapcommon import TILE_MODE_STANDIGS
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_FAR_SYSTEMMAP
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_MAX_STARMAP
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_MIN_STARMAP
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_NEAR_SYSTEMMAP
