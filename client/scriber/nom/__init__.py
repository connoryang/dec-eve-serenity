#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\nom\__init__.py
import uuid
import json
from scriber import httputils
import scriber
import typeutils
import datetime
import logging
log = logging.getLogger('scriber')

class NoteOMatic(object):

    def __init__(self, user_id, header = '', body = '', note_prefab = '', note_template = None, params = None, dialog_show = True, dialog_require = False, body_style = 'alert-info', note_show = True, note_require = False, note_force_copy = False, note_copy_default = False, ticket_show = True, ticket_require = False, ticket_lookup = False, ticket_verify = False, reason_require = False, reason_list = None, close_on_continue = False, on_before_submit = None, uid = None):
        self.uid = uid or uuid.uuid4().hex
        self.header = header
        self.body = body
        self.body_style = body_style
        self.user_id = user_id
        self.dialog_show = dialog_show
        self.dialog_require = dialog_require
        self.note_template = note_template
        self.note_prefab = note_prefab
        self.params = params
        self.note_show = note_show
        self.note_require = note_require
        self.note_force_copy = note_force_copy
        self.note_copy_default = note_copy_default
        self.ticket_show = ticket_show
        self.ticket_require = ticket_require
        self.ticket_lookup = ticket_lookup
        self.ticket_verify = ticket_verify
        self.reason_require = reason_require
        self.reason_list = []
        if reason_list:
            for r in reason_list:
                if isinstance(r, (list, tuple)):
                    if len(r) > 1:
                        self.reason_list.append((r[0], r[1]))
                    else:
                        self.reason_list.append((r[0], r[0]))
                else:
                    self.reason_list.append((r, r))

        self.close_on_continue = close_on_continue
        self.on_before_submit = on_before_submit
        self._reason = None
        self._ticket_id = None
        self._copy_to_zendesk = False
        self._note = None
        self._reference = None
        self._params = {}

    def render_js(self, enabled = True):
        return scriber.scribe('widgets/noteomatic/init_js.html', enabled=enabled, user_id=self.user_id, prefab=self.note_prefab, header=self.header, body=self.body, body_style=self.body_style, dialog_show=self.dialog_show, dialog_require=self.dialog_require, note_show=self.note_show, note_require=self.note_require, note_force_copy=self.note_force_copy, note_copy_default=self.note_copy_default, ticket_show=self.ticket_show, ticket_require=self.ticket_require, ticket_lookup=self.ticket_lookup, ticket_verify=self.ticket_verify, reason_require=self.reason_require, reason_list=self.reason_list, close_on_continue=self.close_on_continue, on_before_submit=self.on_before_submit)

    def render_db(self):
        if self._reason == '-1':
            self._reason = None
        reason_name = self._get_reason_name(self._reason)
        context = {'ticket_id': self._ticket_id,
         'ticket': 'Ticket #%s ' % self._ticket_id if self._ticket_id else None,
         'ticket_link': 'Ticket #%s ' % self._ticket_id if self._ticket_id else None,
         'reason_name': reason_name,
         'reason_value': self._reason,
         'reason': 'Reason: %s (#%s)' % (reason_name, self._reason) if self._reason else None,
         'note': self._note,
         'reference': self._reference,
         'user_id': self.user_id,
         'nl': '\n'}
        if self._params and isinstance(self._params, dict):
            context.update(self._params)
        return scriber.scribe_str(self.note_template, **context)

    def _get_reason_name(self, value):
        if value is None:
            return
        for r in self.reason_list:
            if isinstance(r, (list, tuple)):
                v = r[0]
                if len(r) > 1:
                    n = r[1]
                else:
                    n = r[0]
            else:
                v = r
                n = r
            if v == value:
                return n

        return value

    def save(self, db2_service, gm_id, append_to_note_id = None):
        try:
            schema = db2_service.GetSchema('znote')
            if append_to_note_id:
                res = schema.MultiNotes_Select(append_to_note_id)
                if res and len(res) == 1:
                    old_note = res[0]
                    schema.MultiNotes_Update(append_to_note_id, '%s\n\n--- Appended at %s ---\n\n%s' % (old_note.note, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.render_db()))
                    return append_to_note_id
            return schema.MultiNotes_Insert(30002, self.user_id, self.render_db(), gm_id)
        except Exception as ex:
            log.exception('Error while saving Note: %r' % ex)
            return False

    def feed(self, request):
        req = httputils.parse_request(request)
        self._reason = req.p.str('nom_reason', None)
        self._ticket_id = req.p.int('nom_ticket_id', None)
        self._copy_to_zendesk = req.p.bool('nom_copy_zd')
        self._note = req.p.str('nom_note')
        self._reference = req.p.str('nom_reference')
        self._params = req.p.str('nom_params')
        if self._params:
            self._params = json.loads(self._params)

    def is_valid(self):
        if not self.user_id:
            return False
        if self.note_require and not self._note:
            return False
        if self.ticket_require and not self._ticket_id:
            return False
        if self.reason_require and not self._reason:
            return False
        return True

    def add_params(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._params[k] = v


class PrefabRegistery(object):
    _registery = {}
    _cacheService = None
    _flushTrigger = -1
    _append_window_minutes = 15

    @staticmethod
    def init(cacheService):
        if not PrefabRegistery._cacheService:
            log.info('Initialized Note-o-Matic Prefab Registery')
            PrefabRegistery._cacheService = cacheService
            PrefabRegistery.flush_check()

    @staticmethod
    def get_prefab(prefab_name, user_id):
        PrefabRegistery.flush_check()
        if prefab_name not in PrefabRegistery._registery:
            log.debug('Note-o-Matic Prefab "%s" not in registery... loading it' % prefab_name)
            try:
                data = PrefabRegistery._cacheService.Setting('noteomatic', 'prefab_%s' % prefab_name)
                if not data:
                    log.debug('Note-o-Matic Prefab "prebab_%s" data not found!' % prefab_name)
                    PrefabRegistery._registery[prefab_name] = None
                else:
                    log.debug('Note-o-Matic Prefab "prebab_%s" data from DB settings = %r' % (prefab_name, data))
                    PrefabRegistery._registery[prefab_name] = json.loads(data)
            except Exception as ex:
                log.exception('Failed to load or parse Note-o-Matic Prefab %s: %r' % (prefab_name, ex))
                PrefabRegistery._registery[prefab_name] = None

        if not PrefabRegistery._registery[prefab_name]:
            log.error('Note-o-Matic Prefab %s not found or corrupt' % prefab_name)
            return
        else:
            return NoteOMatic(user_id, note_prefab=prefab_name, **PrefabRegistery._registery[prefab_name])

    @staticmethod
    def is_enabled():
        return typeutils.bool_eval(PrefabRegistery._cacheService.Setting('noteomatic', 'enabled'))

    @staticmethod
    def flush_check():
        fresh_trigger = typeutils.int_eval(PrefabRegistery._cacheService.Setting('noteomatic', 'flush_trigger'))
        if PrefabRegistery._flushTrigger != fresh_trigger:
            log.info('Note-o-Matic Prefab Registery Flushed')
            PrefabRegistery._registery = {}
            PrefabRegistery._flushTrigger = fresh_trigger
            PrefabRegistery._append_window_minutes = typeutils.int_eval(PrefabRegistery._cacheService.Setting('noteomatic', 'append_window_minutes'), 15)

    @staticmethod
    def get_append_window_minutes():
        return PrefabRegistery._append_window_minutes
