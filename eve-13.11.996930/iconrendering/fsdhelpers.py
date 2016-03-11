#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\iconrendering\fsdhelpers.py
import os
import site
import blue
import devenv
site.addsitedir(os.path.abspath(os.path.join(devenv.BRANCHROOT, 'packages')))
import fsdSchemas.binaryLoader as binaryLoader

def LoadFSDFromFile(osPath):
    return binaryLoader.LoadFSDDataInPython(osPath)


def LoadFSDFromResFile(resPath):
    osPath = blue.paths.ResolvePath(resPath)
    return LoadFSDFromFile(osPath)
