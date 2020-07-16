from functools import partial
import json
import os
import sys
from tkinter import Tk, font, Frame, Button

from obswebsocket import obsws, requests


# Changes an internal path variable based on whether the application was built into an EXE or not.
# Will be used for builds later on
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    __location__ = os.path.dirname(sys.executable)
else:
    __location__ = os.path.realpath(os.path.join(os.getcwd(),
                                    os.path.dirname(__file__)))
    

class OBSWebsocketHandler:
    """Class that handles communication with OBS and the websocket"""
    def __init__(self, host, port, password):
        # Setup a websocket connection to OBS
        self.ws = obsws(host, port, password)
        self.ws.connect()

        # Get the scenes from OBS
        self.scenes = self._get_scenes()

    def _get_scenes(self):
        return self.ws.call(requests.GetSceneList()).getScenes()
    
    def change_scene(self, name):
        """Changes the current OBS scene"""
        self.ws.call(requests.SetCurrentScene(name))


class PTZCamSync:
    """Class that handles the general program logic"""
    def __init__(self):
        with open(os.path.join(__location__, "settings.json"), "r") as f:
            self.settings = json.load(f)
        print("Loaded settings from disk.")
        self.ws_handler = OBSWebsocketHandler("127.0.0.1", 4444, self.settings["password"])
        self.ws = self.ws_handler.ws

    def change_scene(self, camera_id, preset_num):
        # Get the camera and scene name
        camera = self._get_camera(camera_id)
        if camera is None:
            print("A camera with the id: {} was not found in the config. "
                  "Please make sure you have it configured correctly.".format(camera_id))
            return
        # Get the scene name
        scene = self._get_scene_for_preset(camera_id, preset_num)
        if scene is None:
            print("An OBS scene was not found for camera ID {} and preset number {}. "
                  "Please make sure you have it configured correctly.".format(camera_id, preset_num))
            return
        # Get the camera's IP address
        address = camera["address"]
        del address
        # Change the OBS Scene
        self.ws_handler.change_scene(scene)
        
    def get_all_cameras(self):
        return [camera for camera in self.settings["cameras"]]

    def _get_camera(self, camera_id):
        for camera in self.settings["cameras"]:
            if camera["id"] == camera_id:
                return camera
        return None

    def _get_scene_for_preset(self, camera_id, preset_num):
        camera = self._get_camera(camera_id)
        for preset in camera["presets"]:
            if preset["preset_num"] == preset_num:
                return preset["obs_scene"]
        return None


if __name__ == "__main__":
    # Main window
    root = Tk("PTZCamSync")
    root.title("PTZCamSync")
    
    # Some constants for use later
    font = font.Font(family="Helvetica Neue", size=14)
    background_color = "#333333"
    btn_background_color = "#655F5F"
    text_color = "#FFFFFF"
    
    # Main window frame
    main_frame = Frame(root, width=100, height=100)
    main_frame.configure(bg=background_color)
    main_frame.pack(fill="both", expand=1)
    
    # Camera management class init. Also starts the websocket
    cam_sync = PTZCamSync()
    cameras = cam_sync.get_all_cameras()
    
    for camera in cameras:
        cam_frame = Frame(main_frame)
        cam_frame.configure(bg=background_color)
        cam_frame.pack(fill="x")
        cam_id = camera["id"]
        # cam_address = camera["address"]
        presets = camera["presets"]
        for preset in presets:
            preset_id = preset["preset_num"]
            title = preset["obs_scene"]
            btn = Button(cam_frame, text=title, font=font, bg=btn_background_color, fg=text_color, command=partial(cam_sync.change_scene, cam_id, preset_id))
            btn.pack(padx=5, pady=5, side="left")

    root.mainloop()
