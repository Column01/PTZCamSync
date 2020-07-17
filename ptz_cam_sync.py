from functools import partial
import json
import os
import requests as req
import sys
from tkinter import Tk, font, Frame, Button

from obswebsocket import obsws, requests, exceptions


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
        print("Trying to connect to OBS...")
        # Setup a websocket connection to OBS
        try:
            self.ws = obsws(host, port, password)
            self.ws.connect()
        except exceptions.ConnectionFailure:
            print("Connection was unsuccessful")
            sys.exit("OBS Must be open in order to use this application")

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
        print("Loading settings from disk...")
        with open(os.path.join(__location__, "settings.json"), "r") as f:
            self.settings = json.load(f)
        self.ws_handler = OBSWebsocketHandler("127.0.0.1", 4444, self.settings["password"])
        self.ws = self.ws_handler.ws
        self.obs_scenes = [x["name"] for x in self.ws_handler.scenes]
        self.camera_preset_url = "http://{address}/cgi-bin/ptzctrl.cgi?ptzcmd&poscall&{preset_num}"

    def change_scene(self, camera_id, preset_num, scene, address):
        # Change the OBS Scene
        self.ws_handler.change_scene(scene)

        # Format the camera control URL
        formatted_url = self.camera_preset_url.format(address=address, preset_num=preset_num)
        # Send camera control message
        try:
            resp = req.post(formatted_url, timeout=0.001)
            if resp.status_code != 200:
                print("Error sending a camera a preset command. "
                      "Camera Address: {}, Preset Num: {}. Status Code: {}".format(address, preset_num, resp.status_code))
        except req.exceptions.RequestException:
            print("There was an error when trying to switch the camera's position. "
                  "This could mean your camera address is wrong or the camera is off. \n"
                  "Camera Address: {}, Preset Num: {}".format(address, preset_num))

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
    main_frame = Frame(root)
    main_frame.configure(bg=background_color)
    main_frame.pack(fill="both", expand=1)

    # Camera management class init. Also starts the websocket
    cam_sync = PTZCamSync()
    cameras = cam_sync.get_all_cameras()
    buttons = []
    # Setup Tkinter buttons to change OBS scenes and change camera presets.
    for camera in cameras:
        cam_frame = Frame(main_frame)
        cam_frame.configure(bg=background_color)
        cam_frame.pack(fill="x")
        cam_id = camera["id"]
        cam_address = camera["address"]
        presets = camera["presets"]
        for preset in presets:
            preset_id = preset["preset_num"]
            scene = preset["obs_scene"]
            if scene in cam_sync.obs_scenes:
                btn = Button(cam_frame, text=scene, font=font, bg=btn_background_color, fg=text_color, command=partial(cam_sync.change_scene, cam_id, preset_id, scene, cam_address))
                btn.pack(padx=5, pady=5, side="left")
                buttons.append(btn)
            else:
                print("The scene \"{}\" was not found in your OBS configuration.".format(scene))

    if len(buttons) == 0:
        sys.exit("Could not find any valid OBS scenes in the config. Please make sure you have them named correctly in the configuration.")
    root.update()
    # Makes width = 200 if it's less than that
    width = root.winfo_width() if root.winfo_width() >= 300 else 300
    height = root.winfo_height()
    root.minsize(width, height)
    # Start the app
    root.mainloop()
