#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\iconrendering\_appsetup.py
import os
import sys
import site
pkgspath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
site.addsitedir(pkgspath)
rootpath = os.path.abspath(os.path.join(pkgspath, '..'))
if rootpath not in sys.path:
    sys.path.append(rootpath)
import binbootstrapper
binbootstrapper.update_binaries(__file__, *binbootstrapper.DLLS_GRAPHICS)
import trinity
from binbootstrapper.trinityapp import create_windowless_device

def CreateTrinityApp():
    create_windowless_device()
    trinity.device.animationTimeScale = 0.0
