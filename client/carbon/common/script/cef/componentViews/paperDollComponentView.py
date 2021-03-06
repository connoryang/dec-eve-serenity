#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\paperDollComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class PaperDollComponentView(BaseComponentView):
    __guid__ = 'cef.PaperDollComponentView'
    __COMPONENT_ID__ = const.cef.PAPER_DOLL_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'PaperDoll'
    __COMPONENT_CODE_NAME__ = 'paperdoll'
    __SHOULD_SPAWN__ = {'client': True}
    GENDER = 'gender'
    DNA = 'dna'
    TYPE_ID = 'typeID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GENDER, None, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetGenderTypesEnum, displayName='Gender')
        cls._AddInput(cls.DNA, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='DNA')
        cls._AddInput(cls.TYPE_ID, 0, cls.RUNTIME, const.cef.COMPONENTDATA_ID_TYPE, displayName='Type ID')

    @staticmethod
    def _GetGenderTypesEnum(*args):
        genderList = []
        genderList.append(('Female', const.FEMALE, 'Female'))
        genderList.append(('Male', const.MALE, 'Male'))
        return genderList


PaperDollComponentView.SetupInputs()
