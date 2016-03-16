#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\siteconst.py
from carbonui.util.color import Color
from utillib import KeyVal
SITE_COLOR_ANOMALY = Color(82, 131, 17)
SITE_COLOR_SIGNATURE = Color(255, 51, 0)
SITE_COLOR_STATIC_SITE = Color(235, 168, 51)
SITE_COLOR_BOOKMARK = Color(41, 181, 191)
SITE_COLOR_CORP_BOOKMARK = Color(41, 181, 191)
SITE_COLOR_MISSION = Color(0, 255, 255)
COMPASS_DIRECTIONS_COLOR = Color(255, 255, 255, 0.9)
COMPASS_SWEEP_COLOR = Color(255, 255, 255, 0.75)
COMPASS_OPACITY_ACTIVE = 0.5
COMPASS_OPACITY_DISABLED = 0.25
SITE_ICON_STATIC_SITE = 'res:/UI/Texture/classes/SensorSuite/diamond2.png'
SITE_OUTER_TEXTURE_STATIC_SITE = ('res:/UI/Texture/classes/SensorSuite/bracket_landmark_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_landmark_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_landmark_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_landmark_4.png')
SITE_ICON_ANOMALY = 'res:/UI/Texture/classes/SensorSuite/diamond2.png'
SITE_OUTER_TEXTURE_ANOMALY = ('res:/UI/Texture/classes/SensorSuite/bracket_anomaly_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_anomaly_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_anomaly_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_anomaly_4.png')
SITE_ICON_SIGNATURE = 'res:/UI/Texture/classes/SensorSuite/diamond2.png'
SITE_OUTER_TEXTURE_SIGNATURE = ('res:/UI/Texture/classes/SensorSuite/bracket_sig_accurate_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_sig_accurate_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_sig_accurate_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_sig_accurate_4.png')
SITE_ICON_BOOKMARK = 'res:/UI/Texture/Icons/38_16_150.png'
SITE_OUTER_TEXTURE_BOOKMARK = ('res:/UI/Texture/classes/SensorSuite/bracket_bookmark_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_4.png')
SITE_ICON_CORP_BOOKMARK = 'res:/UI/Texture/Icons/38_16_257.png'
SITE_OUTER_TEXTURE_CORP_BOOKMARK = ('res:/UI/Texture/classes/SensorSuite/bracket_bookmark_corp_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_corp_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_corp_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_corp_4.png')
SITE_ICON_MISSION = 'res:/UI/Texture/classes/SensorSuite/missions.png'
SITE_OUTER_TEXTURE_MISSION = ('res:/UI/Texture/classes/SensorSuite/bracket_mission_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_mission_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_mission_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_mission_4.png')
SITE_STATIC_SITE = KeyVal(color=SITE_COLOR_STATIC_SITE, outerTextures=SITE_OUTER_TEXTURE_STATIC_SITE, icon=SITE_ICON_STATIC_SITE)
SITE_ANOMALY = KeyVal(color=SITE_COLOR_ANOMALY, outerTextures=SITE_OUTER_TEXTURE_ANOMALY, icon=SITE_ICON_ANOMALY)
SITE_SIGNATURE = KeyVal(color=SITE_COLOR_SIGNATURE, outerTextures=SITE_OUTER_TEXTURE_SIGNATURE, icon=SITE_ICON_SIGNATURE)
SITE_MISSION = KeyVal(color=SITE_COLOR_MISSION, outerTextures=SITE_OUTER_TEXTURE_MISSION, icon=SITE_ICON_MISSION)
SITE_BOOKMARK = KeyVal(color=SITE_COLOR_BOOKMARK, outerTextures=SITE_OUTER_TEXTURE_BOOKMARK, icon=SITE_ICON_BOOKMARK)
SITE_CORP_BOOKMARK = KeyVal(color=SITE_COLOR_CORP_BOOKMARK, outerTextures=SITE_OUTER_TEXTURE_CORP_BOOKMARK, icon=SITE_ICON_CORP_BOOKMARK)
