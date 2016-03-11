#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\graphs\__init__.py


def PrimeGraphData(graphData):
    loadData = []
    for each in graphData:
        if isinstance(each, tuple):
            label, proportion, color = each
            segmentParams = GraphSegmentParams(proportion, color, tooltip=label)
            loadData.append(segmentParams)
        else:
            loadData.append(each)

    return loadData


class GraphSegmentParams(object):

    def __init__(self, proportion, color, tooltip = None, showMarker = False, sizeFactor = 1.0):
        self.proportion = proportion
        self.color = color
        self.tooltip = tooltip
        self.sizeFactor = sizeFactor
        self.showMarker = showMarker
