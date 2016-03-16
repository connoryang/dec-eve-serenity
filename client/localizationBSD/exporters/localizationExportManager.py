#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\exporters\localizationExportManager.py
from .. import const as localizationBSDConst
from . import LocalizationExporterError
from localization.logger import LogError
import blue
import uthread
import log
import carbon.backend.script.bsdWrappers.bsdUtil as bsdUtil
import localizationPickleExporter
import localizationIntFileExporter
import localizationScaleformFileExporter
import localizationXMLResourceExporter
import localizationResxExporter
import localizationYamlFileExporter

class LocalizationExportManager(object):
    _EXPORTERS_MAP = {'.pickle': localizationPickleExporter.LocalizationPickleExporter,
     '.int': localizationIntFileExporter.LocalizationIntFileExporter,
     '.xml': localizationXMLResourceExporter.LocalizationXMLResourceExporter,
     '.resx': localizationResxExporter.LocalizationResxExporter,
     'vita': localizationScaleformFileExporter.LocalizationScaleformFileExporter,
     'yaml': localizationYamlFileExporter.LocalizationYamlFileExporter}

    @classmethod
    def GetExportTypes(cls):
        exporterTypes = []
        for exporterName, exporter in cls._EXPORTERS_MAP.iteritems():
            exporterTypes.append((exporterName, exporter.EXPORT_DESCRIPTION))

        return exporterTypes

    @classmethod
    def GetResourceNamesForAllProjects(cls):
        return cls._CallMethodOnAllProjects(exporterMethodName='GetResourceNamesWithProjectSettings')

    @classmethod
    def GetResourceNamesForProject(cls, projectID):
        return cls._CallMethodOnProject(projectID, exporterMethodName='GetResourceNamesWithProjectSettings')

    @classmethod
    def ExportAllProjects(cls, notificationFunction = None, **kwargs):
        return cls._CallMethodOnAllProjects(internalMethod=cls._ExportOneProject, notificationFunction=notificationFunction, additionalSettings=kwargs)

    @classmethod
    def ExportProject(cls, projectID, **kwargs):
        return cls._CallMethodOnProject(projectID, internalMethod=cls._ExportOneProject, additionalSettings=kwargs)

    @classmethod
    def _GetAllProjectsData(cls):
        dbzlocalization = sm.GetService('DB2').GetSchema('zlocalization')
        getSubmittedOnly = 1
        projectSettings = dbzlocalization.Projects_Select(getSubmittedOnly)
        projectList = bsdUtil.MakeRowDicts(projectSettings, projectSettings.columns)
        return projectList

    @classmethod
    def _GetProjectData(cls, projectID):
        dbzlocalization = sm.GetService('DB2').GetSchema('zlocalization')
        getSubmittedOnly = 1
        projectSettings = dbzlocalization.Projects_SelectByID(getSubmittedOnly, projectID)
        projectList = bsdUtil.MakeRowDicts(projectSettings, projectSettings.columns)
        if len(projectList) != 1:
            LogError("ExportManager's ExportProject method tried to retrieve project of projectID (%s) and instead got result set of (%s) elements." % (projectID, len(projectList)))
            return None
        projectDict = projectList[0]
        return projectDict

    @classmethod
    def _ExportOneProject(cls, projectDict, additionalSettings):
        returnValue = cls._ExecuteExporterMethod(projectDict, 'ExportWithProjectSettings', additionalSettings)
        if returnValue is None:
            LogError("ExportManager's Export Project failed to export projectID (%s). Check project settings." % projectDict[localizationBSDConst.COLUMN_PROJECT_ID])
        return returnValue

    @classmethod
    def _ExecuteExporterMethod(cls, projectDict, methodName, additionalSettings):
        returnValue = None
        exportTypeName = projectDict[localizationBSDConst.COLUMN_EXPORT_NAME]
        projectID = projectDict[localizationBSDConst.COLUMN_PROJECT_ID]
        exportLocation = projectDict[localizationBSDConst.COLUMN_EXPORT_LOCATION]
        exportFileName = projectDict[localizationBSDConst.COLUMN_EXPORT_FILE_NAME]
        if all([exportTypeName, exportLocation, exportFileName]):
            newProjectDict = {}
            for key, value in projectDict.iteritems():
                if key == localizationBSDConst.COLUMN_PROJECT_ID:
                    continue
                if key == localizationBSDConst.COLUMN_EXPORT_LOCATION:
                    value = cls._ResolveInternalPaths(value)
                newProjectDict[key] = value

            if additionalSettings is not None:
                for key, value in additionalSettings.iteritems():
                    newProjectDict[key] = value

            try:
                exporterMethod = getattr(cls._EXPORTERS_MAP[exportTypeName], methodName)
            except (KeyError, AttributeError):
                raise LocalizationExporterError('ExportManager was asked to export using methodName (%s) on invalid Exporter. For projectID (%s); exportTypeName (%s). Check _EXPORTERS_MAP variable.' % (methodName, projectID, exportTypeName))

            returnValue = exporterMethod(projectID, **newProjectDict)
        else:
            raise LocalizationExporterError('ExportManager was asked to export using methodName (%s) with missing exportTypeName Exporter setting. For projectID (%s); exportTypeName (%s). Check Project settings.' % (methodName, projectID, exportTypeName))
        return returnValue

    @classmethod
    def _ResolveInternalPaths(cls, exportLocation):
        if exportLocation and exportLocation.startswith('root:/'):
            exportLocation = blue.paths.ResolvePath(exportLocation)
        return exportLocation

    @classmethod
    def _CallMethodOnAllProjects(cls, internalMethod = None, exporterMethodName = None, notificationFunction = None, additionalSettings = None):
        returnDict = {}
        projectsEntries = cls._GetAllProjectsData()
        for index, projectDict in projectsEntries.iteritems():
            if projectDict[localizationBSDConst.COLUMN_EXPORT_NAME] is not None:
                try:
                    if internalMethod:
                        try:
                            returnValue = internalMethod(projectDict, additionalSettings)
                        except:
                            log.LogException()
                            continue

                    elif exporterMethodName:
                        returnValue = cls._ExecuteExporterMethod(projectDict, exporterMethodName, additionalSettings)
                except Exception as e:
                    log.LogTraceback('Export Manager caught the error: ' + repr(e))
                    continue

                returnDict[projectDict[localizationBSDConst.COLUMN_PROJECT_ID]] = returnValue
                if notificationFunction is not None:
                    notificationParam = {projectDict[localizationBSDConst.COLUMN_PROJECT_ID]: returnValue}
                    uthread.new(notificationFunction, notificationParam).context = 'localizationExportManager::notificationCallback'

        return returnDict

    @classmethod
    def _CallMethodOnProject(cls, projectID, internalMethod = None, exporterMethodName = None, additionalSettings = None):
        projectDict = cls._GetProjectData(projectID)
        if projectDict:
            returnValue = None
            if internalMethod:
                returnValue = internalMethod(projectDict, additionalSettings)
            elif exporterMethodName:
                returnValue = cls._ExecuteExporterMethod(projectDict, exporterMethodName, additionalSettings)
            return returnValue
        else:
            return
