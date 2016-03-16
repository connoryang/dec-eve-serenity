#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\translations.py
import trinity

def GetTranslationValue(obj):
    try:
        return obj.translationCurve.value
    except AttributeError:
        return trinity.TriVectorCurve().value


def SetTranslationValue(obj, pos):
    if hasattr(obj, 'translationCurve') and obj.translationCurve is None:
        obj.translationCurve = trinity.TriVectorCurve()
    obj.translationCurve.value = pos
