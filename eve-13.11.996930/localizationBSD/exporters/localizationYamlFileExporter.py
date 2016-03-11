#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\exporters\localizationYamlFileExporter.py
import zipfile
import os
import yaml
import localizationExporter
from . import LocalizationExporterError

class LocalizationYamlFileExporter(localizationExporter.LocalizationExporterBase):
    EXPORT_DESCRIPTION = 'Exports language data into staticdata files that are used by the DUST vault generation process.'

    @classmethod
    def ExportWithProjectSettingsToZipFileObject(cls, projectID, fileObject, exportFileName, getSubmittedOnly = True, bsdBranchID = None):
        from fsdCommon.fsdYamlExtensions import FsdYamlDumper
        if not exportFileName:
            exportFileName = 'localization-'
        localizationFiles = cls._GetFileContents(projectID, getSubmittedOnly, bsdBranchID)
        exportedFileNames = []
        zipDataFile = zipfile.ZipFile(fileObject, 'w')
        for languageID, messageDict in localizationFiles.iteritems():
            filePath = exportFileName + languageID + '.staticdata'
            zipDataFile.writestr(filePath, yaml.dump(messageDict, allow_unicode=True, Dumper=FsdYamlDumper))
            exportedFileNames.append(filePath)

        zipDataFile.close()
        return (zipDataFile, exportedFileNames)

    @classmethod
    def ExportWithProjectSettings(cls, projectID, exportLocation, exportFileName, getSubmittedOnly = True, **kwargs):
        from fsdCommon.fsdYamlExtensions import FsdYamlDumper
        if not exportLocation or not exportFileName:
            raise LocalizationExporterError('Filepath strings are incomplete. exportLocation, exportFileName: %s, %s.' % (exportLocation, exportFileName))
        localizationFiles = cls._GetFileContents(projectID, getSubmittedOnly)
        exportedFileNames = []
        for languageID, messageDict in localizationFiles.iteritems():
            fileName = exportFileName + languageID + '.staticdata'
            filePath = os.path.abspath(os.path.join(exportLocation, fileName))
            with file(filePath, 'w') as f:
                f.write(yaml.dump(messageDict, allow_unicode=True, Dumper=FsdYamlDumper))
            exportedFileNames.append(filePath)

        return exportedFileNames

    @classmethod
    def _GetFileContents(cls, projectID, getSubmittedOnly, bsdBranchID = None):
        exportData = cls._GetLocalizationMessageDataForExport(projectID, getSubmittedOnly, bsdBranchID=bsdBranchID)
        messagesDict = exportData[1]
        localizationFiles = {}
        for msgID, msg in messagesDict.iteritems():
            msgTextDict = msg.GetAllTextDict()
            for languageID, msgTextRow in msgTextDict.iteritems():
                if languageID not in localizationFiles:
                    localizationFiles[languageID] = {}
                localizationFiles[languageID][msgID] = msgTextRow.text

        return localizationFiles
