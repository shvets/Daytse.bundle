from daytse_service import DaytseService
from plex_storage import PlexStorage

class DaytsePlexService(DaytseService):
    def __init__(self):
        storage_name = Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents', 'daytse.storage'))

        self.queue = PlexStorage(storage_name)

        self.queue.register_simple_type('movie')
        self.queue.register_simple_type('episode')
        self.queue.register_simple_type('season')
        self.queue.register_simple_type('serie')
