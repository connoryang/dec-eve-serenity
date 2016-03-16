#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\iconrendering\nes_cli.py
import logging
import argparse
import os
import sys
import string
import subprocess
import _appsetup
import tempfile
import devenv
import fsdauthoringutils
import stdlogutils
from nes_util import CreateAlpha
from iconrendering import APPNAME
from iconrendering import photo
from evegraphics.utils import CombineSOFDNA
from eveSpaceObject import GetScenePathByRaceName
L = logging.getLogger('iec_cli_%s' % os.getpid())
DEBUG = False
CLEANUP = False
OUTPUT_FOLDER = os.path.join(tempfile.mkdtemp('NES'))
COLORS = (((1.0, 0.0, 0.0), 'R'), ((0.0, 1.0, 0.0), 'G'), ((0.0, 0.0, 1.0), 'B'))

def ParseArgs():
    parser = argparse.ArgumentParser(description='Render space objects for the NES.\nPlease provide a list of typeIDs to render.\nThe renders will be placed in you cache folder and\nan explorer window will open on the folder.\nPlease make sure that the types exist in the release BSD.')
    parser.add_argument('--types', default=[], type=int, nargs='+', help='A list of type ids to render.Example usage: types 123 456 789')
    parser.add_argument('--dna', default=[], type=str, nargs='*', help='A list of dna to render. Example usage: --dna abc1_t1:amarrbase:amarr cb2_t1:noh:caldari')
    parser.add_argument('--cameraYPR', default='', nargs=3, help='An optional camera angle in yaw, pitch and roll radian values. Example usage: --cameraYPR -0.3 0.3 0.0')
    parser.add_argument('--sunDirection', default='', nargs=3, help='An optional sund direction vector.Example usage: --sunDirection 0.0 1.0 0.0')
    parser.add_argument('--debug', default=DEBUG, action='store_true', help='Output debug information.')
    parser.add_argument('--keepsource', action='store_true', help='Set this to keep the source RGB files.')
    return parser.parse_args()


def Main():
    opts = ParseArgs()
    loglevel = logging.DEBUG if opts.debug else logging.INFO
    logging.basicConfig(level=loglevel, filename=stdlogutils.GetTimestampedFilename2(APPNAME), format=stdlogutils.Fmt.NTLM)
    streamh = logging.StreamHandler(sys.stdout)
    streamh.setFormatter(stdlogutils.Fmt.FMT_NTLM)
    L.addHandler(streamh)
    if not opts.types and not opts.dna:
        L.error('No types or dna supplied')
        return
    subprocess.Popen('explorer %s' % OUTPUT_FOLDER.replace('/', '\\'))
    resmapper = fsdauthoringutils.GraphicsCache(devenv.EVEROOT)
    _appsetup.CreateTrinityApp()
    typeIDs = opts.types
    dnas = opts.dna
    if opts.cameraYPR and len(opts.cameraYPR) == 3:
        cameraAngle = map(float, opts.cameraYPR)
    else:
        cameraAngle = None
    if opts.sunDirection and len(opts.sunDirection) == 3:
        sunDirection = map(float, opts.sunDirection)
    else:
        sunDirection = (-0.4592, -0.4602, 0.6614)
    tempRenders = []
    for value in typeIDs + dnas:
        typeID = sofData = None
        if type(value) is int:
            typeID = value
            gID = resmapper.GetGraphicIDForTypeID(typeID)
            sofData = resmapper.GetSOFDataForGraphicID(gID)
            raceName = resmapper.GetSOFDataForGraphicID(gID)[2]
            scenePath = GetScenePathByRaceName(raceName)
            sofDNA = ''
            if all(sofData):
                sofDataForType = resmapper.GetSOFDataForTypeID(typeID)
                sofDNA = CombineSOFDNA(sofAddition=sofDataForType[0], *sofData)
            graphicFile = resmapper.GetGraphicFileForGraphicID(gID)
            name = str(typeID)
        else:
            sofDNA = value
            raceName = sofDNA[2]
            scenePath = GetScenePathByRaceName(raceName)
            graphicFile = None
            name = sofDNA.replace(':', '_').replace('?', '_')
        if not sofDNA and not graphicFile:
            L.error('Type %s does not have a graphicFile nor SOF data' % typeID)
            continue
        sourceFiles = []
        for color, suffix in COLORS:
            outPath = os.path.join(OUTPUT_FOLDER, name + '_' + suffix + '.png')
            L.debug('Rendering %s' % outPath)
            photo.RenderSpaceObject(outPath=outPath, scenePath=scenePath, objectPath=graphicFile, sofDNA=sofDNA, size=512, bgColor=color, transparent=True, cameraAngle=cameraAngle, sunDirection=sunDirection)
            sourceFiles.append(outPath)

        tempRenders.extend(sourceFiles)
        finalPath = os.path.join(OUTPUT_FOLDER, name + u'.png')
        CreateAlpha(finalPath, sourceFiles)

    if not opts.keepsource:
        for filePath in tempRenders:
            os.remove(filePath)


def GetFiles(root):
    return set(map(string.lower, os.listdir(root)))


if __name__ == '__main__':
    try:
        Main()
    except Exception:
        logging.getLogger().error('Unhandled error!', exc_info=True)
        raise
