#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\billboards\billboardsystem.py
import uthread2
import logging
logger = logging.getLogger(__name__)
try:
    from videoplayer import resource
except ImportError:
    resource = None

DYNAMIC_PATH = 'dynamic:/{resourceName}/?video_local={videoResPath}&resource_name={resourceName}'
NO_RESOURCE_PATH = ''

class BillboardResource(object):

    def __init__(self, name, resPathPlaylist):
        self.name = name
        self.resource_path_playlist = [ DYNAMIC_PATH.format(resourceName=name, videoResPath=resPath) for resPath in resPathPlaylist ]
        self.texture_parameters_by_item_id = {}
        self.current_play_index = 0
        resource.register_resource_constructor(name)
        logger.info('Billboard resource %s created', self.name)

    def add_texture_parameters_for_item_id(self, itemID, textureParameters):
        self.texture_parameters_by_item_id[itemID] = textureParameters
        self._set_texture_parameter_resource_paths(self._get_current_resource_path(), textureParameters)

    def remove_texture_parameters_for_item_id(self, itemID):
        self._set_texture_parameter_resource_paths(NO_RESOURCE_PATH, self.texture_parameters_by_item_id[itemID])
        del self.texture_parameters_by_item_id[itemID]

    def reset_video_playback(self):
        self._set_all_texture_parameter_resource_paths(NO_RESOURCE_PATH)

    def play_current_video(self):
        resourcePath = self._get_current_resource_path()
        self._set_all_texture_parameter_resource_paths(resourcePath)

    def _set_all_texture_parameter_resource_paths(self, resourcePath):
        for textureParameters in self.texture_parameters_by_item_id.values():
            self._set_texture_parameter_resource_paths(resourcePath, textureParameters)

    def _set_texture_parameter_resource_paths(self, resourcePath, textureParameters):
        for textureParameter in textureParameters:
            textureParameter.resourcePath = resourcePath

    def _get_current_resource_path(self):
        return self.resource_path_playlist[self.current_play_index]

    def _set_next_resource_path(self):
        self.current_play_index = (self.current_play_index + 1) % len(self.resource_path_playlist)

    def is_unassigned(self):
        return len(self.texture_parameters_by_item_id) == 0

    def play_next_in_playlist(self):
        self._set_next_resource_path()
        self.reset_video_playback()
        self.play_current_video()
        logger.info("resource %s play next video in playlist. new video is number %s '%s'", self.name, self.current_play_index, self._get_current_resource_path())


class BillboardSystem(object):

    def __init__(self):
        self.resources_by_name = {}
        resource.register_state_change_handler(self._on_video_state_change)

    def register_billboard_resource(self, name, playlist, itemId, textureParameters):
        billboard_resource = self.get_billboard_resource(name)
        if billboard_resource is None:
            billboard_resource = BillboardResource(name, playlist)
            self.resources_by_name[name] = billboard_resource
            logging.info("Created a new billboard resourced named '%s'", name)
        billboard_resource.add_texture_parameters_for_item_id(itemId, textureParameters)
        billboard_resource.play_current_video()
        return billboard_resource

    def get_billboard_resource(self, name):
        return self.resources_by_name.get(name)

    def _on_video_state_change(self, videoPlayer, construction_parameters, texture):
        logging.info('video state change. construction params=%s', construction_parameters)
        try:
            if videoPlayer.state != resource.videoplayer.State.DONE:
                logging.warn('not done. construction params=%s', construction_parameters)
                return
            name = construction_parameters.get('resource_name')
            if name is None:
                logging.warning('could not find resource in construction parameters %s', construction_parameters)
                return
            logging.info('found dynamic resource name %s', name)
            billboard_resource = self.get_billboard_resource(name)
            if not billboard_resource:
                logging.warning("unable to locate billboard resource named '%s'" % name)
                return
            uthread2.start_tasklet(billboard_resource.play_next_in_playlist)
        except Exception:
            logger.exception('something is wrong. construction parameters %s', construction_parameters)

    def unregister_billboard_resource(self, name, itemId):
        billboard_resource = self.get_billboard_resource(name)
        billboard_resource.remove_texture_parameters_for_item_id(itemId)
        if billboard_resource.is_unassigned():
            self._remove_billboard_resource(name)

    def _remove_billboard_resource(self, name):
        if name in self.resources_by_name:
            del self.resources_by_name[name]
