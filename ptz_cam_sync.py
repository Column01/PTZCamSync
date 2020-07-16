import json
import sys
import os
from obs_handler import OBSWebsocketHandler

if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    __location__ = os.path.dirname(sys.executable)
else:
    __location__ = os.path.realpath(os.path.join(os.getcwd(),
                                    os.path.dirname(__file__)))


class PTZCamSync:
    def __init__(self):
        with open(os.path.join(__location__, "settings.json"), "r") as f:
            self.settings = json.load(f)
        print("Loaded settings from disk.")
        self.ws_handler = OBSWebsocketHandler("127.0.0.1", 4444, self.settings["password"])
        self.ws = self.ws_handler.ws
    
    def change_scene(self, camera_id, preset_num):
        camera = self._get_camera(camera_id)
        scene = self._get_scene_for_preset(camera, preset_num)
        # address = camera["address"]
        self.ws_handler.change_scene(scene)

    def _get_camera(self, camera_id):
        for camera in self.settings["cameras"]:
            if camera["id"] == camera_id:
                return camera
        return None
    
    def _get_scene_for_preset(self, camera, preset_num):
        for preset in camera["presets"]:
            if preset["preset_num"] == preset_num:
                return preset["obs_scene"]
        
 
if __name__ == "__main__":
    cam_sync = PTZCamSync()
    cam_sync.change_scene("1", "1")
