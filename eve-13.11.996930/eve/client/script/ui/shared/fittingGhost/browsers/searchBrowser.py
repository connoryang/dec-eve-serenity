#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\searchBrowser.py
from collections import defaultdict
from eve.client.script.ui.shared.fittingGhost.browsers.browserUtil import GetTypesByMetaGroups, ShoulAddMetaGroupFolder, GetMetaGroupNameAndEntry, GetScrollListFromTypeListInNodedata, GetScrollListFromTypeList
from eve.client.script.ui.shared.fittingGhost.browsers.filtering import GetValidTypeIDs
from eve.client.script.ui.control import entries as listentry
import localization
from utillib import KeyVal
specialItemGroups = (const.metaGroupStoryline,
 const.metaGroupFaction,
 const.metaGroupOfficer,
 const.metaGroupDeadspace)

class SearchBrowserListProvider(object):

    def __init__(self, searchFittingHelper, onDropDataFunc):
        self.searchFittingHelper = searchFittingHelper
        self.onDropDataFunc = onDropDataFunc

    def GetSearchResults(self):
        marketGroups = sm.GetService('marketutils').GetMarketGroups()
        typeIDs = self.searchFittingHelper.GetSearcableTypeIDs(marketGroups)
        searchTerm = settings.user.ui.Get('fitting_hardwareSearchField', '')
        if not searchTerm:
            return []
        scrollList = []
        validTypeIDs = GetValidTypeIDs(typeIDs, self.searchFittingHelper)
        allMarketGroups = marketGroups[None]
        myCategories, typeIDsByCategoryID = self.GetCategoryDicts(allMarketGroups, validTypeIDs)
        if len(typeIDsByCategoryID) > 1:
            scrollList += self.GetSearchCatagoryEntries(typeIDsByCategoryID, myCategories)
        else:
            for categoryID, categoryTypeIDs in typeIDsByCategoryID.iteritems():
                fakeNodeData = KeyVal(typeIDs=categoryTypeIDs, sublevel=-1, categoryID=categoryID)
                results = self.GetSeachCategorySubContent(fakeNodeData)
                scrollList.extend(results)

        return scrollList

    def GetCategoryDicts(self, allMarketGroups, validTypeIDs):
        typeIDsByCategoryID = defaultdict(list)
        myCategories = {}
        for typeID in validTypeIDs:
            topMarketCategory = self.searchFittingHelper.GetMarketCategoryForType(typeID, allMarketGroups)
            if topMarketCategory is None:
                continue
            typeIDsByCategoryID[topMarketCategory.marketGroupID].append(typeID)
            myCategories[topMarketCategory.marketGroupID] = topMarketCategory

        return (myCategories, typeIDsByCategoryID)

    def GetSearchCatagoryEntries(self, typeIDsByCategoryID, myCategories):
        scrollList = []
        for categoryID, categoryTypeIDs in typeIDsByCategoryID.iteritems():
            category = myCategories[categoryID]
            data = {'GetSubContent': self.GetSeachCategorySubContent,
             'label': category.marketGroupName,
             'id': ('searchGroups', categoryID),
             'showlen': 0,
             'sublevel': 0,
             'state': 'locked',
             'BlockOpenWindow': True,
             'categoryID': category.marketGroupID,
             'typeIDs': categoryTypeIDs,
             'iconID': category.iconID,
             'hint': category.description}
            group = listentry.Get('Group', data)
            scrollList.append(group)

        return scrollList

    def GetSeachCategorySubContent(self, nodedata, *args):
        typeIDs = nodedata.typeIDs
        typesByMetaGroupID = GetTypesByMetaGroups(typeIDs)
        categoryID = nodedata.categoryID
        scrollList = []
        for metaGroupID, typeIDList in sorted(typesByMetaGroupID.items()):
            shoulAddMetaGroupFolder = ShoulAddMetaGroupFolder(metaGroupID)
            if shoulAddMetaGroupFolder:
                metaGroupLabelAndEntry = self.GetSearchSubGroup(metaGroupID, typeIDList, nodedata=nodedata, categoryID=categoryID)
                scrollList.append(metaGroupLabelAndEntry)
            else:
                standardTypes = GetScrollListFromTypeList(typeIDList, -1, self.onDropDataFunc)
                for entry in standardTypes:
                    scrollList.append((' %s' % entry.label, entry))

        scrollList = [ item[1] for item in localization.util.Sort(scrollList, key=lambda x: x[0]) ]
        return scrollList

    def GetSearchSubGroup(self, metaGroupID, typeIDList, nodedata = 0, categoryID = None, *args):
        labelAndEntry = GetMetaGroupNameAndEntry(metaGroupID, typeIDList, nodedata, subContentFunc=GetScrollListFromTypeListInNodedata, onDropDataFunc=self.onDropDataFunc, idTuple=('fittingSearchGroups', (metaGroupID, categoryID)))
        return labelAndEntry
