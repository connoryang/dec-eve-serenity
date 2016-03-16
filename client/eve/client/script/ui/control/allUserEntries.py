#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\allUserEntries.py


def AllUserEntries():
    return ['listentry.User',
     'listentry.Sender',
     'listentry.ChatUser',
     'listentry.SearchedUser',
     'listentry.AgentEntry',
     'listentry.ChatUserSimple',
     'listentry.WatchListEntry',
     'listentry.FleetMember',
     'listentry.FleetHeader',
     'listentry.FleetCompositionEntry',
     'listentry.ChannelACL']


exports = {'uiutil.AllUserEntries': AllUserEntries}
