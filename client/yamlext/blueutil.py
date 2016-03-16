#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\yamlext\blueutil.py
import yaml
import blue
import pytelemetry.zoning as telemetry

@telemetry.ZONE_FUNCTION
def ReadYamlFile(path):
    telemetry.APPEND_TO_ZONE(path)
    data = None
    if blue.paths.exists(path):
        rf = blue.ResFile()
        rf.Open(path)
        yamlStr = rf.read()
        rf.close()
        data = yaml.load(yamlStr, Loader=yaml.CLoader)
    return data
