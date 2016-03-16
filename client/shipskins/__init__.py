#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipskins\__init__.py
from .static import License, Skin, SkinMaterial, SkinStaticData
from .storage import AppliedSkinStorage, LicensedSkin, LicensedSkinStorage, SkinAlreadyLicensed, SkinNotLicensed
from util import repr, Base
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
