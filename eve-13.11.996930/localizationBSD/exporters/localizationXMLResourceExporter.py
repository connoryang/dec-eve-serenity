#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\exporters\localizationXMLResourceExporter.py
import xml.etree.ElementTree
import os
import zipfile
from . import LocalizationExporterError
import localizationExporter

class LocalizationXMLResourceExporter(localizationExporter.LocalizationExporterBase):
    EXPORT_DESCRIPTION = 'Exports language data into .xml file, that is then used by Launcher (or any other non-game client) to load language strings.\nWhere:\nexportLocation    - location of folder under which the resource xml file is created\nexportFileName    - name of the language resource file to write.'
    FILE_EXT = '.xml'
    XML_TEXT_ROOT = 'TextResource'
    XML_LANGUAGES = 'languages'
    XML_LANGUAGE = 'language'
    XML_LANGUAGE_ID = 'languageID'
    XML_LANGUAGE_NAME = 'name'
    XML_TRANSLATED_NAME = 'translatedName'
    XML_TEXTS = 'texts'
    XML_MESSAGE = 'message'
    XML_LABEL = 'label'
    XML_TEXT = 'text'
    XML_STRING = 'string'

    @classmethod
    def ExportWithProjectSettingsToZipFileObject(cls, projectID, fileObject, exportFileName, getSubmittedOnly = True, bsdBranchID = None):
        if not exportFileName:
            exportFileName = 'localization'
        rootElement = cls._CreateXMLElements(projectID, getSubmittedOnly)
        textsElementTree = xml.etree.ElementTree.ElementTree(rootElement)
        zipDataFile = zipfile.ZipFile(fileObject, 'w')

        class dummy:
            pass

        data = []
        f = dummy()
        f.write = data.append
        textsElementTree.write(f, 'utf-8', xml_declaration=True)
        data = ''.join(data)
        zipDataFile.writestr(exportFileName + '.xml', data)
        zipDataFile.close()
        return (zipDataFile, [exportFileName + '.xml'])

    @classmethod
    def ExportWithProjectSettings(cls, projectID, exportLocation, exportFileName, getSubmittedOnly = True, **kwargs):
        if not exportLocation or not exportFileName:
            raise LocalizationExporterError('Filepath strings are incomplete. exportLocation, exportFileName: %s, %s.' % (exportLocation, exportFileName))
        exportedFilenames = []
        rootElement = cls._CreateXMLElements(projectID, getSubmittedOnly)
        textsElementTree = xml.etree.ElementTree.ElementTree(rootElement)
        try:
            exportedFilenames = [os.path.join(exportLocation, exportFileName + cls.FILE_EXT)]
            textsElementTree.write(exportedFilenames[0], encoding='utf-8', xml_declaration=True)
        except TypeError as anError:
            newMessage = "Is there perhaps an attribute on XML Element with None value? ElementTree doesn't like that."
            raise TypeError(anError.args, newMessage)

        return exportedFilenames

    @classmethod
    def _CreateXMLElements(cls, projectID, getSubmittedOnly):
        exportData = cls._GetLocalizationMessageDataForExport(projectID, getSubmittedOnly)
        folderPathToLabelsIndex = exportData[0]
        messagesDict = exportData[1]
        languageCodesResultSet = exportData[2]
        rootElement = xml.etree.ElementTree.Element(tag=cls.XML_TEXT_ROOT)
        languagesElement = xml.etree.ElementTree.Element(cls.XML_LANGUAGES)
        rootElement.append(languagesElement)
        langDict = sm.GetService('cache').Rowset(const.cacheLocalizationLanguages).Index('languageID')
        for aLanguage in languageCodesResultSet:
            try:
                langName = langDict[aLanguage.languageID].languageName
            except KeyError:
                langName = 'Unknown language %s' % aLanguage.languageID

            attributes = {cls.XML_LANGUAGE_ID: aLanguage.languageID,
             cls.XML_LANGUAGE_NAME: langName}
            languagesElement.append(xml.etree.ElementTree.Element(cls.XML_LANGUAGE, attrib=attributes))

        textElement = xml.etree.ElementTree.Element(cls.XML_TEXTS)
        rootElement.append(textElement)
        for messageID, messageObj in sorted(messagesDict.iteritems(), key=lambda x: x[1].labelPath):
            messageElement = xml.etree.ElementTree.Element(cls.XML_MESSAGE, attrib={cls.XML_LABEL: messageObj.labelPath})
            textElement.append(messageElement)
            for languageID, textRow in messageObj.GetAllTextDict().iteritems():
                stringElement = xml.etree.ElementTree.Element(cls.XML_TEXT, attrib={cls.XML_LANGUAGE_ID: languageID,
                 cls.XML_STRING: textRow.text})
                messageElement.append(stringElement)

        return rootElement

    @classmethod
    def GetResourceNamesWithProjectSettings(cls, projectID, exportLocation, exportFileName, getSubmittedOnly = True, **kwargs):
        return [os.path.join(exportLocation, exportFileName + cls.FILE_EXT)]
