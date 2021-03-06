#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\zaction\zactionCommon.py
import GameWorld
import log
import carbon.common.script.sys.service as service
import collections
import inspect
import ztree
import uthread
import stackless

class ActionComponent:
    __guid__ = 'zaction.ActionComponent'

    def __init__(self, state):
        self.rootID = 0
        self.treeInstance = None
        self.treeState = None
        self.stepState = None
        self.sharedState = None
        self.TreeInstanceID = const.ztree.GENERATE_TREE_INSTANCE_ID
        self.defaultAction = None
        if boot.role == 'client':
            action = sm.GetService('zactionClient').defaultAction
        else:
            action = sm.GetService('zactionServer').GetDefaultStartingAction()
        try:
            self.defaultAction = state.get(const.zactionConst.ACTIONTREE_RECIPE_DEFAULT_ACTION_NAME, action)
            if self.defaultAction is None:
                self.defaultAction = action
            self.defaultAction = int(self.defaultAction)
        except:
            log.LogException()
            self.defaultAction = action

    def GetDefaultAction(self):
        return self.defaultAction


class zactionCommonBase(service.Service):
    __guid__ = 'zaction.zactionCommonBase'

    def __init__(self, treeManager):
        self.treeManager = treeManager
        self.createDebugItems = False
        service.Service.__init__(self)

    def SetupActionTree(self, mySystemID):
        self.rootNode = GameWorld.ActionTreeNode()
        self.rootNode.ID = 0
        self.rootNode.name = 'Root'
        self.rootNode.CreateMyPropertyList()
        self.treeManager.AddTreeNode(self.rootNode)
        for treeNode in cfg.treeNodes:
            if mySystemID == treeNode.systemID:
                node = GameWorld.ActionTreeNode()
                node.ID = treeNode.treeNodeID
                node.name = str(treeNode.treeNodeName)
                node.actionType = treeNode.treeNodeType or 0
                node.CreateMyPropertyList()
                if not self.treeManager.AddTreeNode(node):
                    log.LogError('Failed to add tree node to ActionTree', node.treeNodeName)

        for linkRowSet in cfg.treeLinks.itervalues():
            for link in linkRowSet:
                if mySystemID == link.systemID:
                    if link.linkType is not None:
                        linkType = link.linkType & const.zactionConst._ACTION_LINK_TYPE_BIT_FILTER
                        exposureType = link.linkType >> const.zactionConst._ACTION_LINK_BIT_ORDER_SPLIT
                    else:
                        linkType = 0
                        exposureType = 0
                    if not self.treeManager.AddTreeLink(linkType, exposureType, link.parentTreeNodeID, link.childTreeNodeID):
                        log.LogError('Failed to add tree link to ActionTree', link.parentTreeNodeID, link.childTreeNodeID)

        import actionProcTypes
        import zaction
        import carbon.common.script.zaction.zactionCommon as zactionCommon
        procList = inspect.getmembers(actionProcTypes)
        for procName, procDef in procList:
            if isinstance(procDef, zaction.ProcTypeDef) or isinstance(procDef, zactionCommon.ProcTypeDef):
                for entry in procDef.properties:
                    if isinstance(entry, zaction.ProcPropertyTypeDef) or isinstance(entry, zactionCommon.ProcPropertyTypeDef):
                        GameWorld.AddActionProcNameMappingInfo(procName, entry.name, entry.isPrivate)

                if procDef.pythonProc is not None:
                    GameWorld.RegisterPythonActionProc(procName, procDef.pythonProc[0], procDef.pythonProc[1])

        for prop in cfg.treeNodeProperties:
            treeNode = self.treeManager.GetTreeNodeByID(prop.treeNodeID)
            if treeNode is not None:
                if prop.procID is None or 0 == prop.procID:
                    propertyName = prop.propertyName
                else:

                    def GetMangledName(propName, procInstanceID):
                        nameLen = len(propName)
                        mangleName = '___' + str(procInstanceID)
                        mangleNameLen = len(mangleName)
                        if nameLen + mangleNameLen > const.zactionConst.MAX_PROP_NAME_LEN:
                            baseLen = const.zactionConst.MAX_PROP_NAME_LEN - mangleNameLen
                            propName = propName[:baseLen]
                        finalName = propName + mangleName
                        return finalName

                    propertyName = GetMangledName(prop.propertyName, prop.procID)
                if False == treeNode.AddProperty(propertyName, prop.propertyBaseType, prop.propertyValue):
                    log.LogError('Failed to add ' + str(propertyName) + ' to node ' + str(treeNode.name) + ' ID ' + str(prop.treeNodeID))

        for stepList in cfg.actionTreeSteps.itervalues():
            for step in stepList:
                treeNode = self.treeManager.GetTreeNodeByID(step.actionID)
                if treeNode is not None:
                    type = step.stepType or const.zactionConst.ACTIONSTEP_TYPEID_NORMAL
                    loc = step.stepLocation or const.zactionConst.ACTIONSTEP_LOCID_CLIENTSERVER
                    treeNode.AddActionStep(str(step.stepName), step.stepID, type, loc)

        for stepList in cfg.actionTreeSteps.itervalues():
            for step in stepList:
                treeNode = self.treeManager.GetTreeNodeByID(step.actionID)
                if treeNode is not None:
                    if step.stepParent is not None:
                        treeNode.ConnectActionStepChildren(step.stepParent, step.stepID)
                    if step.stepSibling is not None:
                        treeNode.ConnectActionStepSiblings(step.stepSibling, step.stepID)

        for procList in cfg.actionTreeProcs.itervalues():
            for proc in procList:
                treeNode = self.treeManager.GetTreeNodeByID(proc.actionID)
                if treeNode is not None:
                    if proc.stepID is not None and proc.stepID != 0:
                        stepNode = treeNode.GetActionStepByID(proc.stepID)
                        if stepNode is None:
                            log.LogError('Failed to find step node referenced by ActionProc: ', proc.actionID, proc.stepID, proc.procType)
                        else:
                            stepNode.AddActionProcRecord(str(proc.procType), proc.procID, proc.isMaster)
                    else:
                        treeNode.AddActionProcRecord(str(proc.procType), proc.procID, proc.isMaster)

    def GetActionTree(self):
        return self.treeManager

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Current Action'] = '?'
        actionTreeNode = component.treeInstance.GetCurrentTreeNode()
        if actionTreeNode and component.treeInstance.debugItem:
            report['Current Action'] = '%s  duration: %f' % (actionTreeNode.name, component.treeInstance.debugItem.duration)
        else:
            report['Current Action'] = actionTreeNode.name
        return report

    def ResetTree(self):
        log.LogWarn('%s: Action Tree Reset Initiated.' % self.__guid__)
        self.treeManager.PrepareForReload()
        self.SetupActionTree(self.GetTreeSystemID())
        self.treeManager.EnableTreeInstances()
        log.LogWarn('%s: Action Tree Reset Finished.' % self.__guid__)


class zactionCommon(zactionCommonBase):
    __guid__ = 'zaction.zactionCommon'

    def __init__(self, treeManager):
        zactionCommonBase.__init__(self, treeManager)
        GameWorld.SetBasePythonActionProcMethod(ZactionCommonBasePythonProcMethod)
        self.actionTickManager = GameWorld.ActionTickManager()
        self.defaultAction = 0

    @classmethod
    def GetTreeSystemID(cls):
        return const.ztree.TREE_SYSTEM_ID_DICT[const.zactionConst.ACTION_SCHEMA]

    def ProcessAnimationDictionary(self, animationDict):
        GameWorld.processAnimInfoYAML(animationDict)


def ZactionCommonBasePythonProcMethod(method, args, blocking):
    if blocking:
        callbackHandle = GameWorld.GetResultHandleForCurrentPythonProc()

        def _CallBlockingMethod():
            result = method(*args)
            GameWorld.SetResultForPythonProcFromHandle(callbackHandle, int(result))

        thread = uthread.new(_CallBlockingMethod)
        thread.localStorage['callbackHandle'] = callbackHandle
        return False
    else:
        try:
            with uthread.BlockTrapSection():
                result = method(*args)
        except:
            log.LogException()
            result = False

        return result


def GetPropertyForCurrentPythonProc(propName):
    return GameWorld.GetPropertyForCurrentPythonProc(propName, stackless.getcurrent().localStorage.get('callbackHandle'))


def AddPropertyForCurrentPythonProc(propDict):
    GameWorld.AddPropertyForCurrentPythonProc(propDict, stackless.getcurrent().localStorage.get('callbackHandle'))


class ProcTypeDef(object):
    __guid__ = 'zaction.ProcTypeDef'

    def __init__(self, procCategory = None, isMaster = True, isConditional = False, properties = [], displayName = None, pythonProc = None, description = None, stepLocationRequirements = None, stepTypeRequirements = None, invalidProcDef = False):
        self.isMaster = isMaster
        self.isConditional = isConditional
        self.properties = properties
        self.procCategory = procCategory
        self.displayName = displayName
        self.pythonProc = pythonProc
        self.stepLocationRequirements = stepLocationRequirements
        if not stepTypeRequirements:
            if isConditional:
                stepTypeRequirements = const.zactionConst.ACTION_STEP_TYPE_CONDITIONALS
            else:
                stepTypeRequirements = const.zactionConst.ACTION_STEP_TYPE_NORMALS
        self.stepTypeRequirements = stepTypeRequirements
        self.description = description
        self.invalidProcDef = invalidProcDef


class ProcPropertyTypeDef(object):
    __guid__ = 'zaction.ProcPropertyTypeDef'

    def __init__(self, name, dataType, userDataType = None, isPrivate = True, displayName = None, default = None, show = True):
        self.name = name
        self.dataType = dataType
        self.userDataType = userDataType
        self.isPrivate = isPrivate
        self.displayName = displayName
        self.default = default
        self.show = show


def _ProcNameHelper(displayName, procRow):
    import actionProperties
    import actionProcTypes
    import re
    import types
    propDict = actionProperties.GetPropertyValueDict(procRow)
    procDef = actionProcTypes.GetProcDef(procRow.procType)
    propDefs = procDef.properties

    def InterpretSub(match):
        name = re.search('\\((.*?)\\)', match.group(0))
        propName = name.group(1)
        if propName not in propDict:
            return '(ERR: ' + propName + ')'
        propRows = ztree.NodeProperty.GetAllPropertiesByTreeNodeID(procRow.actionID)
        for propRow in propRows:
            if propRow.propertyName == propName:
                for propDef in propDefs:
                    if propDef.name == propName:
                        dictVal = propDict[propName]
                        subString = str(dictVal)
                        if propDef.userDataType != None:
                            typeInfo = getattr(actionProperties, propDef.userDataType, None)
                            if typeInfo is not None and types.TupleType == type(typeInfo):
                                if 'listMethod' == typeInfo[0]:
                                    list = typeInfo[1](propRow)
                                elif 'list' == typeInfo[0]:
                                    list = typeInfo[1]
                                else:
                                    list = None
                                for tuple in list:
                                    name, val, desc = tuple[:3]
                                    if val == dictVal:
                                        subString = str(name)
                                        break

                        return subString

                break

        return '(ERR: ' + propName + ')'

    return re.sub('(%\\(.*?\\).)', InterpretSub, displayName)


def ProcNameHelper(displayName):
    return lambda procRow: _ProcNameHelper(displayName, procRow)


exports = {'zaction.ProcNameHelper': ProcNameHelper,
 'zaction.GetPropertyForCurrentPythonProc': GetPropertyForCurrentPythonProc,
 'zaction.AddPropertyForCurrentPythonProc': AddPropertyForCurrentPythonProc}
