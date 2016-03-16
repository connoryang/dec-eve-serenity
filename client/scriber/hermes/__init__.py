#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\hermes\__init__.py
import datetime
import uuid
import json
import typeutils
import logging
log = logging.getLogger('hermes')

class UpdateListener(object):

    def __init__(self, user_id, stamp):
        self.user_id = user_id
        self.stamp = stamp
        self.is_triggered = False
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()

    def __str__(self):
        return '<UpdateListener:user_id=%s, stamp=%s, is_triggered=%s, id=%s>' % (self.user_id,
         self.stamp,
         self.is_triggered,
         id(self))


class ReadStatus(object):

    def __init__(self, is_shown = False, is_read = False, is_closed = False, is_dismissed = False):
        self.is_shown = is_shown
        self.is_read = is_read
        self.is_closed = is_closed
        self.is_dismissed = is_dismissed


class HermesError(Exception):
    pass


class NotificationError(HermesError):
    pass


class NotificationNotFound(NotificationError):
    pass


class NotificationUpdateError(NotificationError):
    pass


class NotificationDismissError(NotificationError):
    pass


class Notification(object):
    TYPE_INFO = 1
    TYPE_WARNING = 2
    TYPE_ALERT = 3
    PERSISTENCE_SILENT = 1
    PERSISTENCE_QUICK = 2
    PERSISTENCE_STICKY = 3

    def __init__(self, title, body = None, icon = None, notification_type = None, persistence = None, on_click = None, sender = None, notification_id = None, expires = None, can_dismiss = True, is_shared = False, on_respond = None, hide_recipients = False, channels = None):
        self.title = title
        self.body = body
        self.icon = icon
        self.notification_type = notification_type or Notification.TYPE_INFO
        self.persistence = persistence or Notification.PERSISTENCE_QUICK
        self.on_click = on_click
        self.sender = sender
        self.expires = expires
        self.can_dismiss = can_dismiss
        self.is_shared = is_shared
        self.on_respond = on_respond
        self.hide_recipients = hide_recipients
        self.channel_list = []
        self._parse_channels(channels)
        self.notification_id = notification_id or uuid.uuid4().hex
        self.created = datetime.datetime.now()
        self.who_is_on_it = None
        self.response_datetime = None
        self.shared_dismiss = False
        self._to_users = None
        self._to_user_types = None
        self._to_user_roles = None
        self._read_status_map = {}
        self.update_stamp = 0

    def update_notification(self, notification):
        self.title = notification.title
        self.body = notification.body
        self.icon = notification.icon
        self.notification_type = notification.notification_type
        self.persistence = notification.persistence
        self.on_click = notification.on_click
        self.sender = notification.sender
        self.expires = notification.expires
        self.can_dismiss = notification.can_dismiss
        self.is_shared = notification.is_shared
        self.on_respond = notification.on_respond
        self.who_is_on_it = notification.who_is_on_it
        self.response_datetime = notification.response_datetime
        self.shared_dismiss = notification.shared_dismiss
        self.hide_recipients = notification.hide_recipients
        self.channel_list = notification.channel_list

    def to_dict(self, user_id = None, quotes_to_html = False):
        fixed_body = self.body
        fixed_title = self.title
        if quotes_to_html:
            fixed_body = fixed_body.replace('"', '&quot;')
            fixed_title = fixed_title.replace('"', '&quot;')
        buff_map = {'title': unicode(fixed_title),
         'body': unicode(fixed_body) if self.body else '',
         'icon': self.icon,
         'notification_type': self.notification_type,
         'persistence': self.persistence,
         'on_click': self.on_click,
         'expires': None if not isinstance(self.expires, datetime.datetime) else self.expires.isoformat(),
         'can_dismiss': self.can_dismiss,
         'is_shared': self.is_shared,
         'on_respond': self.on_respond,
         'notification_id': self.notification_id,
         'created': self.created.isoformat(),
         'who_is_on_it': unicode(self.who_is_on_it),
         'response_datetime': self.response_datetime,
         'hide_recipients': self.hide_recipients,
         'sender': unicode(self.sender) if self.body else '',
         'update_stamp': self.update_stamp,
         'channels': self.channel_list}
        if not self.hide_recipients:
            buff_map['to_users'] = self._to_users
            buff_map['to_user_types'] = self._to_user_types
            buff_map['to_user_roles'] = self._to_user_roles
            buff_map['is_global'] = self.is_global()
        if user_id:
            buff_map['is_shown'] = self.is_shown(user_id)
            buff_map['is_read'] = self.is_read(user_id)
            buff_map['is_closed'] = self.is_closed(user_id)
            buff_map['is_dismissed'] = self.is_dismissed(user_id)
        return buff_map

    def to_json(self, user_id = None):
        return json.dumps(self.to_dict(user_id))

    def mark_shown(self, user_id):
        if user_id not in self._read_status_map:
            self._read_status_map[user_id] = ReadStatus()
        self._read_status_map[user_id].is_shown = True

    def mark_read(self, user_id):
        if user_id not in self._read_status_map:
            self._read_status_map[user_id] = ReadStatus()
        self._read_status_map[user_id].is_read = True

    def mark_closed(self, user_id):
        if user_id not in self._read_status_map:
            self._read_status_map[user_id] = ReadStatus()
        self._read_status_map[user_id].is_closed = True

    def mark_dismissed(self, user_id):
        if user_id not in self._read_status_map:
            self._read_status_map[user_id] = ReadStatus()
        self._read_status_map[user_id].is_shown = True
        self._read_status_map[user_id].is_dismissed = True

    def is_expired(self):
        if self.expires:
            return self.expires < datetime.datetime.now()
        return False

    def is_global(self):
        return not self._to_users and not self._to_user_types and not self._to_user_roles

    def is_shown(self, user_id):
        if user_id in self._read_status_map:
            return self._read_status_map[user_id].is_shown
        return False

    def is_read(self, user_id):
        if user_id in self._read_status_map:
            return self._read_status_map[user_id].is_read
        return False

    def is_closed(self, user_id):
        if user_id in self._read_status_map:
            return self._read_status_map[user_id].is_closed
        return False

    def is_dismissed(self, user_id):
        if user_id in self._read_status_map:
            return self._read_status_map[user_id].is_dismissed
        return False

    def in_channels(self, channel_list):
        if self.channel_list:
            for channel in channel_list:
                if channel in self.channel_list:
                    return True

            return False
        else:
            return True

    def _parse_channels(self, channels):
        if channels:
            if not isinstance(channels, (list, tuple)):
                channels = [str(channels)]
            for chan in channels:
                parts = chan.split('.')
                for i, chan_part in enumerate(parts):
                    cc = [chan_part]
                    while i > 0:
                        i -= 1
                        cc.append(parts[i])

                    cc.reverse()
                    sub_chan = '.'.join(cc)
                    if sub_chan not in self.channel_list:
                        self.channel_list.append(sub_chan)

    def __repr__(self):
        return '<Notification: id=%s, title="%s">' % (self.notification_id, self.title)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, Notification):
            return self.notification_id == other.notification_id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.notification_id)


class Hermes(object):

    def __init__(self, listener_limit = 10):
        self.notification_map = {}
        self._by_user_id = {}
        self._by_user_type = {}
        self._by_user_role = {}
        self._global_notification_list = []
        now = datetime.datetime.now()
        self._update_trigger = (now.year % 2000 * 1000 + now.month * 10 + now.day) * 1000000
        self._update_listeners = {}
        self._listener_limit = listener_limit
        log.info('Hermes::__init__(listener_limit=%s) - _update_trigger=%s' % (listener_limit, self._update_trigger))

    def send_notification(self, notification, users = None, user_types = None, user_role_masks = None):
        log.info('Hermes::send_notification() users=%s, user_types=%s, user_role_masks=%s, notification=%s' % (users,
         user_types,
         user_role_masks,
         notification.to_json()))
        old_notification = self.get_notification(notification.notification_id)
        if old_notification:
            self.cancel_notification(old_notification)
        notification.update_stamp = self._update_trigger
        self.notification_map[notification.notification_id] = notification
        if not users and not user_types and not user_role_masks:
            self._global_notification_list.append(notification)
        else:
            if users:
                self._send_to_users(notification, users)
            if user_types:
                self._send_to_user_types(notification, user_types)
            if user_role_masks:
                self._send_to_user_roles(notification, user_role_masks)
        self.trigger_update()

    def update_notification(self, notification):
        log.info('Hermes::update_notification() notification=%s' % notification.to_json())
        if notification:
            if notification.notification_id not in self.notification_map:
                raise NotificationUpdateError('Notification not found: notification_id=%s' % notification.notification_id)
            self.notification_map[notification.notification_id].update_notification(notification)
            self.trigger_update()

    def get_notification(self, notification_id):
        if notification_id in self.notification_map:
            return self.notification_map[notification_id]

    def cancel_notification(self, notification_or_id):
        notification = self._id_to_notification(notification_or_id)
        log.debug('Hermes::cancel_notification() notification=%s' % notification.to_json())
        if notification:
            remove_buffer = []
            if notification in self._global_notification_list:
                self._global_notification_list.remove(notification)
            for notification_batch in (self._by_user_id, self._by_user_type, self._by_user_role):
                for key, notification_list in notification_batch.iteritems():
                    if notification in notification_list:
                        notification_list.remove(notification)
                    if not notification_list:
                        remove_buffer.append((key, notification_batch))

            if notification.notification_id in self.notification_map:
                del self.notification_map[notification.notification_id]
            for key, dict_ref in remove_buffer:
                del dict_ref[key]

            self.trigger_update()

    def get_notification_list(self, user_id, user_type, user_role_mask, channel_list = None):
        notification_list = []
        expired_list = []
        channel_list = channel_list or []
        for notification_batch in (self._get_by_user_id(user_id),
         self._get_by_user_type(user_type),
         self._get_by_user_role_masks(user_role_mask),
         self._global_notification_list):
            for notification in notification_batch:
                if notification.is_expired():
                    expired_list.append(notification.notification_id)
                elif not notification.is_dismissed(user_id) and notification not in notification_list:
                    if notification.in_channels(channel_list):
                        notification_list.append(notification)

        for notification_id in expired_list:
            self.cancel_notification(notification_id)

        notification_list.sort(key=lambda n: n.created, reverse=True)
        return notification_list

    def last_trigger(self):
        return self._update_trigger

    def mark_read(self, notification_or_id, user_id):
        notification = self._id_to_notification(notification_or_id)
        if not notification:
            raise NotificationNotFound('No notification with identifier "%s" was found' % notification_or_id)
        log.info('Hermes::mark_read(notification_id=%s, user_id=%s)' % (notification.notification_id, user_id))
        if notification.is_expired():
            self.cancel_notification(notification)
        else:
            notification.mark_read(user_id)
        self.trigger_update()
        return True

    def mark_closed(self, notification_or_id, user_id):
        notification = self._id_to_notification(notification_or_id)
        if not notification:
            raise NotificationNotFound('No notification with identifier "%s" was found' % notification_or_id)
        if notification.is_expired():
            self.cancel_notification(notification)
        else:
            notification.mark_closed(user_id)
        self.trigger_update()
        return True

    def respond(self, notification_or_id, user_id):
        notification = self._id_to_notification(notification_or_id)
        if not notification:
            raise NotificationNotFound('No notification with identifier "%s" was found' % notification_or_id)
        if notification.is_shared and notification.who_is_on_it:
            return notification.who_is_on_it
        if notification.is_expired():
            self.cancel_notification(notification)
        else:
            notification.mark_read(user_id)
            notification.mark_closed(user_id)
            notification.response_datetime = datetime.datetime.now()
            notification.who_is_on_it = user_id
        self.trigger_update()
        return user_id

    def dismiss(self, notification_or_id, user_id):
        notification = self._id_to_notification(notification_or_id)
        if not notification:
            raise NotificationNotFound('No notification with identifier "%s" was found' % notification_or_id)
        log.info('Hermes::dismiss(notification_id=%s, user_id=%s)' % (notification.notification_id, user_id))
        if not notification.can_dismiss:
            raise NotificationDismissError('This notification can not be dismissed')
        if notification.is_expired() or notification.is_shared:
            self.cancel_notification(notification)
        else:
            notification.mark_dismissed(user_id)
        self.trigger_update()
        return True

    def get_listener(self, user_id, stamp):
        if user_id not in self._update_listeners:
            self._update_listeners[user_id] = UpdateListener(user_id, stamp)
        self._update_listeners[user_id].updated = datetime.datetime.now()
        return self._update_listeners[user_id]

    def remove_listener(self, update_listener):
        if update_listener.user_id in self._update_listeners:
            del self._update_listeners[update_listener.user_id]

    def trigger_listeners(self):
        for user_id, listener in self._update_listeners.items():
            if listener.stamp < self._update_trigger:
                self.remove_listener(listener)
                listener.is_triggered = True

    def trigger_update(self):
        self._update_trigger += 1
        self.trigger_listeners()

    def _id_to_notification(self, notification_or_id):
        if isinstance(notification_or_id, Notification):
            notification_or_id = notification_or_id.notification_id
        return self.get_notification(notification_or_id)

    def _get_by_user_id(self, user_id):
        if user_id in self._by_user_id:
            return self._by_user_id[user_id]
        return []

    def _get_by_user_type(self, user_type):
        if user_type in self._by_user_type:
            return self._by_user_type[user_type]
        return []

    def _get_by_user_role_masks(self, role_masks):
        buff = []
        role_list = self._extract_role_list(role_masks)
        for role in role_list:
            if role in self._by_user_role:
                buff.extend(self._by_user_role[role])

        return buff

    def _send_to_users(self, notification, users):
        if not hasattr(users, '__iter__'):
            users = [users]
        for user_id in users:
            if user_id not in self._by_user_id:
                self._by_user_id[user_id] = []
            self._by_user_id[user_id].append(notification)

        notification._to_users = users

    def _send_to_user_types(self, notification, user_types):
        if not hasattr(user_types, '__iter__'):
            user_types = [user_types]
        for user_type in user_types:
            if user_type not in self._by_user_type:
                self._by_user_type[user_type] = []
            self._by_user_type[user_type].append(notification)

        notification._to_user_types = user_types

    def _send_to_user_roles(self, notification, user_role_masks):
        role_list = self._extract_role_list(user_role_masks)
        for role in role_list:
            if role not in self._by_user_role:
                self._by_user_role[role] = []
            self._by_user_role[role].append(notification)

        notification._to_user_roles = role_list

    @staticmethod
    def _extract_role_list(user_role_masks):
        role_list = []
        if not hasattr(user_role_masks, '__iter__'):
            user_role_masks = [user_role_masks]
        for role_mask in user_role_masks:
            role_list.extend(typeutils.split_bitmask(role_mask))

        return list(set(role_list))
