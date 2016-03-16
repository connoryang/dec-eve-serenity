#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\sys\clientStatsSvc.py
import service
import sys
import os
import blue
import telemetry
import cPickle
import uthread
import log
import time
import trinity
import yaml
import zlib
import util
import datetime
import evegraphics.settings as gfxsettings
from clientStatsCommon import *
BLUE_STATS_NAMES = {'Trinity/FrameTimeAbove100ms': (int, 'frameTimeAbove100ms', False),
 'Trinity/FrameTimeAbove200ms': (int, 'frameTimeAbove200ms', False),
 'Trinity/FrameTimeAbove300ms': (int, 'frameTimeAbove300ms', False),
 'Trinity/FrameTimeAbove400ms': (int, 'frameTimeAbove400ms', False),
 'Trinity/FrameTimeAbove500ms': (int, 'frameTimeAbove500ms', False),
 'Trinity/FrameTime/ActiveMean': (float, 'frameTimeMean', False),
 'Trinity/FrameTime/ActiveStdDev': (float, 'frameTimeStdDev', False),
 'Blue/Memory/Python': (long, 'memoryPython', True),
 'Blue/Memory/Malloc': (long, 'memoryMalloc', True),
 'Blue/Memory/WorkingSet': (long, 'memoryWorkingSet', True),
 'Blue/Memory/PageFileUsage': (long, 'memoryPageFileUsage', True),
 'Blue/resMan/LoadObject': (float, 'loadObject', False),
 'Blue/resMan/LoadObjectCalls': (int, 'loadObjectCalls', False),
 'Blue/resMan/LoadObjectCacheHit': (int, 'loadObjectCacheHits', False),
 'Blue/resMan/LoadObjectShared': (int, 'loadObjectShared', False),
 'Blue/resMan/GetResourceCalls': (int, 'getResourceCalls', False),
 'Blue/resMan/GetResourceCacheHit': (int, 'getResourceCacheHits', False),
 'Blue/resMan/GetResourceShared': (int, 'getResourceShared', False),
 'Blue/logInfo': (int, 'logInfo', False),
 'Blue/logNotice': (int, 'logNotice', False),
 'Blue/logWarn': (int, 'logWarn', False),
 'Blue/logErr': (int, 'logErr', False),
 'Blue/BlueRemoteStream/BytesDownloaded': (int, 'bytesDownloaded', False),
 'Blue/BlueRemoteStream/PretransferTime': (float, 'pretransferTime', False),
 'Blue/BlueRemoteStream/DownloadTime': (float, 'downloadTime', False),
 'Blue/RemoteFileCache/FailedPrimary': (int, 'failedDownloadsPrimary', False),
 'Blue/RemoteFileCache/FailedBackup': (int, 'failedDownloadsSecondary', False),
 'Blue/RemoteFileCache/CorruptDownloads': (int, 'corruptDownloads', False),
 'Blue/RemoteFileCache/CorruptFiles': (int, 'corruptFiles', False),
 'Blue/TimesliceWarnings': (int, 'timesliceWarnings', False)}

class ClientStatsSvc(service.Service):
    __guid__ = 'svc.clientStatsSvc'
    __notifyevents__ = ['OnClientReady',
     'OnDisconnect',
     'OnProcessLoginProgress',
     'ProcessShutdown',
     'DoSessionChanging',
     'OnViewStateChanged']
    __displayname__ = 'Client Statistics Service'
    __dependencies__ = ['machoNet']

    def __init__(self):
        service.Service.__init__(self)
        self.entries = {}
        self.currentState = STATE_STARTUP
        self.version = 2
        self.stateMask = 0
        self.lastStageSampleTime = time.clock()
        self.hasEnteredGame = 0
        self.hasProcessedExit = False
        self.statsEntries = {}
        self.clientStatsMaxBatch = 5
        self.fileStarted = False
        self.filename = os.path.join(blue.paths.ResolvePathForWriting(u'cache:/clientStats.dat'))
        if os.path.exists(self.filename):
            setattr(self, 'prevContents', self.ReadFile(self.filename))
        else:
            self.SampleStats(STATE_UNINITIALIZEDSTART)

    def Run(self, memStream = None):
        self.sessionFilePath = blue.paths.ResolvePathForWriting('cache:/%d_%d.session' % (blue.os.pid, session.sid))
        try:
            self.LogInfo('Creating session file at', self.sessionFilePath)
            self.sessionFile = open(self.sessionFilePath, 'w')
            blue.SetCrashSessionFileDescriptor(self.sessionFile.fileno())
        except OSError:
            log.LogException()
            sys.exc_clear()

        try:
            self.osPlatform = PLATFORM_WINDOWS
            if blue.sysinfo.isTransgaming:
                self.osPlatform = PLATFORM_MACOS
            elif blue.sysinfo.isWine:
                if blue.sysinfo.wineHostOs.startswith('Darwin'):
                    self.osPlatform = PLATFORM_MACOS_WINE
                else:
                    self.osPlatform = PLATFORM_LINUX_WINE
        except Exception:
            pass

        self.statsWaitingToBeSent = []
        self.lastClientState = 'None'
        self.otherClients = 0
        for key, value in BLUE_STATS_NAMES.iteritems():
            name = value[1]
            self.statsEntries[name] = blue.statistics.Find(key)

        self.frameTimeStat = blue.statistics.Find('Trinity/FrameTime')
        self.browserRequestsStat = None
        self.adapterInfo = trinity.adapters.GetAdapterInfo(trinity.adapters.DEFAULT_ADAPTER)
        self.otherRunningClients = 0
        self.crashedClients = 0
        self.state = service.SERVICE_RUNNING
        self.SampleStats(STATE_STARTUP)
        self.timeWhenStateEntered = blue.os.GetWallclockTime()
        blue.statistics.ResetPeaks()
        blue.statistics.ResetDerived()

    def Stop(self, ms):
        self.LogInfo('ClientStatsSvc::Stop - Sampling')
        self.OnProcessExit()
        self.LogInfo('ClientStatsSvc::Stop - DONE')
        service.Service.Stop(self)

    def ReadFile(self, filename):
        try:
            filein = file(filename, 'r')
            datain = cPickle.load(filein)
            return datain
        except Exception as e:
            log.LogException('Error reading file')
            sys.exc_clear()
        finally:
            filein.close()

    @telemetry.ZONE_METHOD
    def SendContentsToServer(self, contents = None):
        try:
            if not sm.services['machoNet'].IsConnected():
                return
        except:
            sys.exc_clear()
            return

        if contents is None:
            contents = self.prevContents
        if contents is None or contents[0] != self.version:
            contents = {}
        else:
            contents = contents[1]
        build = boot.GetValue('build', None)
        contentType = CONTENT_TYPE_PREMIUM
        operatingSystem = PLATFORM_WINDOWS
        if blue.sysinfo.isTransgaming:
            operatingSystem = PLATFORM_MACOS
        blendedContents = self.entries
        blendedStateMask = self.stateMask
        self.entries = dict()
        self.stateMask = 0
        if contents.has_key(STATE_DISCONNECT):
            blendedContents[STATE_DISCONNECT] = contents[STATE_DISCONNECT]
            blendedStateMask += STATE_DISCONNECT
        if contents.has_key(STATE_GAMESHUTDOWN):
            blendedContents[STATE_GAMESHUTDOWN] = contents[STATE_GAMESHUTDOWN]
            blendedStateMask += STATE_GAMESHUTDOWN
        header = (self.version,
         blendedStateMask,
         build,
         operatingSystem,
         contentType)
        data = (header, blendedContents)
        try:
            uthread.Lock(self, 'sendContents')
            if hasattr(self, 'prevContents'):
                delattr(self, 'prevContents')
            return True
        finally:
            uthread.UnLock(self, 'sendContents')

    def Persist(self):
        if not self.fileStarted and os.path.exists(self.filename):
            os.remove(self.filename)
        outfile = file(self.filename, 'w')
        data = (self.version, self.entries)
        cPickle.dump(data, outfile)
        self.fileStarted = True

    @telemetry.ZONE_METHOD
    def SampleStats(self, state):
        self.currentState = state
        try:
            uthread.Lock(self, 'sampleStats')
            if self.entries.has_key(state):
                stats = self.entries[state]
            else:
                stats = {}
            lastStageSampleTime = self.lastStageSampleTime
            self.lastStageSampleTime = time.clock()
            stats[STAT_TIME_SINCE_LAST_STATE] = int((self.lastStageSampleTime - lastStageSampleTime) * 1000)
            if state < STATE_GAMEEXITING:
                stats[STAT_MACHONET_AVG_PINGTIME] = self.GetMachoPingTime()
            if len(blue.pyos.cpuUsage) > 0:
                memdata = blue.pyos.cpuUsage[-1][2]
                if len(memdata) >= 2:
                    stats[STAT_PYTHONMEMORY] = memdata[0]
                else:
                    stats[STAT_PYTHONMEMORY] = 0L
            else:
                stats[STAT_PYTHONMEMORY] = 0L
            cpuProcessTime = blue.sysinfo.GetProcessTimes()
            cpuProcessTime = cpuProcessTime.userTime + cpuProcessTime.systemTime
            stats[STAT_CPU] = int(cpuProcessTime * 10000000.0)
            self.entries[state] = stats
            self.stateMask = self.stateMask + state
            if not hasattr(self, 'prevContents'):
                self.Persist()
            blue.SetCrashKeyValues(u'ClientStatsState', unicode(SHORT_STATE_STRINGS.get(state, u'Unknown')))
        except Exception as e:
            log.LogException('Error while sampling clientStats')
            sys.exc_clear()
        finally:
            uthread.UnLock(self, 'sampleStats')

    def GetMachoPingTime(self):
        if sm.services['machoNet'] is not None and sm.services['machoNet'].IsConnected():
            numSamples = 5
            totalTime = 0
            for i in range(numSamples):
                stat = sm.services['machoNet'].Ping(1, silent=True)
                startTime = stat[0][1]
                endTime = stat[-1][1]
                took = endTime - startTime
                totalTime += took
                blue.pyos.BeNice()

            return totalTime / numSamples
        else:
            return -1

    @telemetry.ZONE_METHOD
    def OnProcessExit(self):
        if not self.hasProcessedExit:
            self.hasProcessedExit = True
            self.SampleStats(STATE_GAMESHUTDOWN)
            try:
                self.sessionFile.write('- shutdown\n')
                self.sessionFile.flush()
                finalStats = self.CaptureStats()
                finalStats['shutdown'] = 1
                finalPackage = self.PrepareStatsPackage(self.lastClientState, finalStats)
                statsSent = False
                try:
                    if session.charid and sm.GetService('machoNet').IsConnected():
                        self.LogInfo('Sending final stats')
                        sm.ProxySvc('eventLog').LogClientStats(session.sid, session.locationid, [finalPackage], isShutdown=True)
                        statsSent = True
                except:
                    log.LogException()
                    sys.exc_clear()

                if statsSent:
                    self.LogInfo('Removing session file', self.sessionFilePath)
                    self.sessionFile.close()
                    os.remove(self.sessionFilePath)
                else:
                    self.LogInfo('Storing client stats in session file')
                    contents = yaml.dump(finalPackage)
                    checksum = zlib.crc32(contents)
                    self.sessionFile.write(contents)
                    self.sessionFile.close()
                    closedSessionFilePath = blue.paths.ResolvePathForWriting('cache:/closed%d_%x.session' % (blue.os.pid, checksum))
                    os.rename(self.sessionFilePath, closedSessionFilePath)
                    self.LogInfo('Session file renamed to', closedSessionFilePath)
            except:
                log.LogException()
                sys.exc_clear()

    @telemetry.ZONE_METHOD
    def OnClientReady(self, *args):
        clientState = args[0]
        if clientState == 'login':
            self.SampleStats(STATE_LOGINWINDOW)
            self.lastClientState = clientState
        elif clientState == 'charsel':
            uthread.new(self.GatherStats, self.lastClientState, session.locationid)
            self.SampleStats(STATE_CHARSELECTION)
            self.lastClientState = clientState
        elif clientState in ('inflight', 'station', 'hangar'):
            if not self.hasEnteredGame:
                uthread.new(self.GatherStats, self.lastClientState, session.locationid)
                self.SampleStats(STATE_GAMEENTERED)
                self.hasEnteredGame = 1
                if hasattr(self, 'prevContents'):
                    uthread.new(self.SendContentsToServer)
            if clientState in ('station', 'hangar'):
                if self.lastClientState in ('station', 'hangar') and clientState != self.lastClientState:
                    uthread.new(self.GatherStats, self.lastClientState, session.locationid)
                elif self.lastClientState == 'charCustomization':
                    uthread.new(self.GatherStats, self.lastClientState, session.locationid)
            self.lastClientState = clientState

    def OnViewStateChanged(self, oldState, newState):
        if newState == 'charactercreation':
            uthread.new(self.GatherStats, self.lastClientState, session.locationid)
            if oldState in ('station', 'hangar'):
                self.lastClientState = 'charCustomization'
            else:
                self.lastClientState = newState

    def OnLoginStarted(self):
        self.SampleStats(STATE_LOGINSTARTED)

    def OnDisconnect(self, reason = 0, msg = ''):
        self.SampleStats(STATE_DISCONNECT)

    def OnProcessLoginProgress(self, *args):
        if args[0] == 'loginprogress::gettingbulkdata' and STATE_BULKDATASTARTED not in self.entries:
            self.SampleStats(STATE_BULKDATASTARTED)
        elif args[0] == 'loginprogress::gettingbulkdata' and STATE_BULKDATASTARTED in self.entries and args[2] == args[3]:
            self.SampleStats(STATE_BULKDATADONE)
        elif args[0] == 'loginprogress::done':
            self.SampleStats(STATE_LOGINDONE)
        elif args[0] == 'loginprogress::connecting':
            self.SampleStats(STATE_LOGINSTARTED)

    def ProcessShutdown(self):
        self.OnProcessExit()

    def OnFatalDesync(self):
        if not self.entries.has_key(self.currentState):
            self.entries[self.currentState] = {}
        if self.entries[self.currentState].has_key(STAT_FATAL_DESYNCS):
            self.entries[self.currentState][STAT_FATAL_DESYNCS] += 1
        else:
            self.entries[self.currentState][STAT_FATAL_DESYNCS] = 1

    def OnRecoverableDesync(self):
        if not self.entries.has_key(self.currentState):
            self.entries[self.currentState] = {}
        if self.entries[self.currentState].has_key(STAT_RECOVERABLE_DESYNCS):
            self.entries[self.currentState][STAT_RECOVERABLE_DESYNCS] += 1
        else:
            self.entries[self.currentState][STAT_RECOVERABLE_DESYNCS] = 1

    def BuildCrashInfo(self, build, uploadResult, sid):
        crashInfo = [build,
         uploadResult,
         sid,
         self.adapterInfo.vendorID,
         self.adapterInfo.deviceID,
         self.adapterInfo.driverVersion,
         self.osPlatform,
         blue.sysinfo.os.majorVersion,
         blue.sysinfo.os.minorVersion,
         blue.sysinfo.os.buildNumber,
         boot.build]
        return crashInfo

    @telemetry.ZONE_METHOD
    def ValidateCrashData(self, crashData, sid):
        try:
            crashKwd = crashData[0]
            if crashKwd == 'shutdown':
                return ['shutdown']
            userid = crashData[1]
            clientid = crashData[2]
            timeStamp = crashData[3]
            build = crashData[4]
            dumpId = crashData[5]
            uploadResult = crashData[6]
            if crashKwd != 'crashed':
                return None
            if build < 0:
                return None
            if len(dumpId) != 36:
                return None
            parts = dumpId.split('-')
            if len(parts) != 5:
                return None
            if len(parts[0]) != 8:
                return None
            if len(parts[1]) != 4:
                return None
            if len(parts[2]) != 4:
                return None
            if len(parts[3]) != 4:
                return None
            if len(parts[4]) != 12:
                return None
            if uploadResult < -1 or uploadResult > 3:
                return None
            crashInfo = self.BuildCrashInfo(build, uploadResult, sid)
            return [dumpId,
             userid,
             clientid,
             util.FmtDateEng(timeStamp, 'sl'),
             crashInfo]
        except:
            return None

    def ReadSavedStats(self, pathOnDisk, checksum):
        package = None
        f = open(pathOnDisk)
        try:
            self.LogInfo('Found session file from an earlier session - reading stats data')
            contents = f.read()
            contentsChecksum = zlib.crc32(contents)
            if checksum == contentsChecksum:
                package = yaml.load(contents)
                if package is None:
                    self.LogInfo('No stats data found')
                elif package[0] in ('login', 'charsel'):
                    package = None
            else:
                self.LogInfo('Invalid session file')
        except Exception:
            log.LogException()
            sys.exc_clear()
            package = None
        finally:
            f.close()

        return package

    @telemetry.ZONE_METHOD
    def ScanSessionFiles(self):
        packagesToSend = []
        crashesToSend = []
        numClients = 0
        crashedClients = 0
        exeFilePids = blue.os.GetExeFilePids()
        files = blue.paths.listdir('cache:/')
        for each in files:
            if each.endswith('.session'):
                baseName = each[:-8]
                pathOnDisk = blue.paths.ResolvePath('cache:/' + each)
                if baseName.startswith('closed'):
                    baseName = baseName[6:]
                    try:
                        pid, checksum = baseName.split('_')
                        checksum = int(checksum, 16)
                        package = self.ReadSavedStats(pathOnDisk, checksum)
                        if package:
                            packagesToSend.append(package)
                    except ValueError:
                        pass
                    finally:
                        try:
                            os.remove(pathOnDisk)
                        except OSError:
                            pass

                else:
                    pid = 0
                    sid = 0
                    try:
                        pidString, sidString = baseName.split('_')
                        pid = int(pidString)
                        sid = long(sidString)
                    except ValueError:
                        pass

                    if pid == blue.os.pid or pid in exeFilePids:
                        numClients += 1
                    else:
                        crashData = None
                        if pid:
                            self.LogInfo('Process %d exited abnormally' % pid)
                            crashedClients += 1
                            foundCrashData = False
                            f = open(pathOnDisk)
                            try:
                                crashData = yaml.load(f)
                                crashData = self.ValidateCrashData(crashData, sid)
                                if crashData:
                                    foundCrashData = True
                                    if crashData[0] == 'shutdown':
                                        crashData = None
                                    else:
                                        self.LogInfo('Found crash info:', crashData[0], crashData[1], crashData[2], crashData[3])
                            except Exception:
                                log.LogException()
                                sys.exc_clear()
                            finally:
                                f.close()

                            if not foundCrashData:
                                sr = os.stat(pathOnDisk)
                                dt = datetime.datetime.fromtimestamp(sr.st_ctime)
                                timestamp = dt.strftime('%Y.%m.%d %H:%M:%S')
                                crashData = ['',
                                 0,
                                 0,
                                 timestamp,
                                 self.BuildCrashInfo(0, -1, sid)]
                        try:
                            os.remove(pathOnDisk)
                        except OSError:
                            crashData = None

                        if crashData:
                            crashesToSend.append(crashData)

        if numClients > 1:
            self.otherClients = numClients - 1
            self.LogInfo('Found %d other clients' % self.otherClients)
        else:
            self.otherClients = 0
            self.LogInfo('Found no other clients')
        if crashedClients > 0:
            self.crashedClients += crashedClients
            self.LogInfo('Found evidence of %d crashed clients (%d total found from session start)' % (crashedClients, self.crashedClients))
        return (packagesToSend, crashesToSend)

    @telemetry.ZONE_METHOD
    def GatherStats(self, event, locationID):
        self.LogInfo('Gathering stats:', event)
        stats = self.CaptureStats()
        if session.charid:
            package = []
            for each in self.statsWaitingToBeSent:
                oldEvent = each[0]
                stats = each[1]
                package.append(self.PrepareStatsPackage(oldEvent, stats))

            self.statsWaitingToBeSent = []
            package.append(self.PrepareStatsPackage(event, stats))
            oldStats, crashes = self.ScanSessionFiles()
            package += oldStats
            del package[self.clientStatsMaxBatch:]
            sm.ProxySvc('eventLog').LogClientStats(session.sid, locationID, package, crashes)
        else:
            self.statsWaitingToBeSent.append((event, stats))

    @telemetry.ZONE_METHOD
    def DoSessionChanging(self, isremote, session, change):
        if 'locationid' not in change or change['locationid'][0] is None:
            return
        uthread.new(self.GatherStats, self.lastClientState, session.locationid)

    @telemetry.ZONE_METHOD
    def PrepareStatsPackage(self, event, stats):
        try:
            charid = session.charid or 0
        except AttributeError:
            charid = 0

        try:
            userid = session.userid or 0
            blue.SetCrashUserId(userid)
        except AttributeError:
            userid = 0

        try:
            sid = session.sid
            blue.SetCrashSessionId(sid)
        except AttributeError:
            sid = 0

        package = [event,
         charid,
         userid,
         sid,
         util.FmtDateEng(blue.os.GetWallclockTime(), 'sl'),
         stats.values()]
        return package

    @telemetry.ZONE_METHOD
    def CaptureStats(self):
        stats = ClientStatsDict()
        is_transgaming = blue.sysinfo.isTransgaming
        stats['gpuVendorId'] = self.adapterInfo.vendorID
        stats['gpuDeviceId'] = self.adapterInfo.deviceID
        stats['gpuDriverVersion'] = self.adapterInfo.driverVersion
        stats['osPlatform'] = self.osPlatform
        stats['eveBuild'] = boot.build
        if not is_transgaming:
            stats['osMajor'] = blue.sysinfo.os.majorVersion
            stats['osMinor'] = blue.sysinfo.os.minorVersion
        else:
            versionEx = blue.win32.TGGetSystemInfo()
            stats['osMajor'] = int(versionEx.get('platform_major_version', 0))
            stats['osMinor'] = int(versionEx.get('platform_minor_version', 0))
        stats['osBuild'] = blue.sysinfo.os.buildNumber
        otherClients = len(blue.os.GetExeFilePids()) - 1
        if otherClients < 0:
            otherClients = 0
        stats['otherClients'] = otherClients
        stats['windowed'] = sm.GetService('device').IsWindowed()
        stats['deviceWidth'] = trinity.device.width
        stats['deviceHeight'] = trinity.device.height
        stats['presentInterval'] = trinity.device.presentationInterval
        stats['hdr'] = gfxsettings.Get(gfxsettings.GFX_HDR_ENABLED)
        stats['antiAliasing'] = gfxsettings.Get(gfxsettings.GFX_ANTI_ALIASING)
        stats['postProcessingQuality'] = gfxsettings.Get(gfxsettings.GFX_POST_PROCESSING_QUALITY)
        stats['shaderQuality'] = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)
        stats['textureQuality'] = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
        stats['lodQuality'] = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY)
        stats['shadowQuality'] = gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY)
        stats['interiorGraphicsQuality'] = gfxsettings.Get(gfxsettings.GFX_INTERIOR_GRAPHICS_QUALITY)
        stats['interiorShaderQuality'] = gfxsettings.Get(gfxsettings.GFX_INTERIOR_SHADER_QUALITY)
        stats['audioEnabled'] = sm.GetService('audio').IsActivated()
        timeInState = blue.os.GetWallclockTime() - self.timeWhenStateEntered
        if timeInState < 0:
            timeInState = 0L
        timeInState = blue.os.TimeAsDouble(timeInState)
        stats['timeInState'] = timeInState
        stats['frameTimePeak'] = self.frameTimeStat.peak
        for value in BLUE_STATS_NAMES.itervalues():
            valueType, valueName, wantPeakValue = value
            statsEntry = self.statsEntries[valueName]
            statsValue = valueType(statsEntry.value)
            stats[valueName] = statsValue
            if wantPeakValue:
                peakValue = valueType(statsEntry.peak)
                stats[valueName + 'Peak'] = peakValue
            statsEntry.Set(0)

        if self.browserRequestsStat is None:
            self.browserRequestsStat = blue.statistics.Find('browser/numRequests')
        if self.browserRequestsStat is not None:
            stats['browserRequests'] = int(self.browserRequestsStat.value)
            self.browserRequestsStat.Set(0)
        self.timeWhenStateEntered = blue.os.GetWallclockTime()
        blue.statistics.ResetPeaks()
        blue.statistics.ResetDerived()
        stats['trinityPlatform'] = trinity.device.GetRenderingPlatformID()
        return stats
