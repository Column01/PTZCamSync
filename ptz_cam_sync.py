import json
import os
import sys
from functools import partial
from tkinter import Button, Frame, Menu, Tk, font, Label

from obswebsocket import exceptions, obsws, requests

from ptz_visca import PTZViscaSocket

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
            do_exit("OBS Must be open in order to use this application")

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
        # Load settings and init cameras
        self.load_settings()
        
        # Connect to obs and collect scenes
        self.ws_handler = OBSWebsocketHandler("127.0.0.1", 4444, self.settings["password"])
        self.ws = self.ws_handler.ws
        self.obs_scenes = [x["name"] for x in self.ws_handler.scenes]

        # Connect to all the cameras
        self._cam_sockets = {camera["address"]: PTZViscaSocket(camera["address"]) for camera in self.cameras}

    def change_scene(self, preset_num, scene, address):
        # Change the OBS Scene
        self.ws_handler.change_scene(scene)
        
        # Connect to the camera and send a control message
        ptz_visca = self._cam_sockets.get(address)
        if ptz_visca is not None:
            if ptz_visca.is_connected:
                sent = ptz_visca.change_preset(preset_num)
                if not sent:
                    print("Error sending a camera a preset command. "
                          "Camera Address: {}, Preset Num: {}".format(address, preset_num))
        else:
            print("No camera socket found with address: {}".format(address))

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
    
    def _handle_close(self):
        for camera in self.cameras:
            address = camera.get("address")
            if address is None:
                continue
            ptz_visca = self._cam_sockets.get(address)
            if ptz_visca is not None:
                ptz_visca.close()
        do_exit("Closing gracefully...")
    
    def load_settings(self):
        """ Loads settings into self.settings and collects a list of cameras into self.cameras
        """
        print("Loading settings from disk...")
        with open(os.path.join(__location__, "settings.json"), "r") as f:
            self.settings = json.load(f)
            f.close()
        self.cameras = self.get_all_cameras()


def do_exit(message):
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        print(message)
        input("Press ENTER to exit...")
        sys.exit()
    else:
        print(message)
        sys.exit()


class MainPTZWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master

        self.master.title("PTZCamSync")
        # Some constants for use later
        self.font = font.Font(family="Helvetica Neue", size=14)
        self.background_color = "#333333"
        self.btn_background_color = "#655F5F"
        self.text_color = "#FFFFFF"

        # Camera management class init. Also starts the websocket
        self.cam_sync = PTZCamSync()
        self.master.protocol("WM_DELETE_WINDOW", self.cam_sync._handle_close)
        # Makes width = 200 if it's less than that
        width = self.master.winfo_width() if self.master.winfo_width() >= 300 else 300
        height = self.master.winfo_height()
        self.master.minsize(width, height)
        menu_bar = Menu(self.master)
        file_bar = Menu(menu_bar, tearoff=False)
        file_bar.add_command(label="Exit", command=self.master.quit)

        menu_bar.add_command(label="Reload Window", command=self.init_window)
        self.master.config(menu=menu_bar)
        self.main_frame = None
        self.init_window()

    def init_window(self):
        if self.main_frame is None:
            # Main window frame
            self.main_frame = Frame(self.master)
            self.main_frame.configure(bg=self.background_color)
            self.main_frame.pack(fill="both", expand=1)
        else:
            self.main_frame.destroy()
            self.cam_sync.load_settings()
            self.main_frame = Frame(self.master)
            self.main_frame.configure(bg=self.background_color)
            self.main_frame.pack(fill="both", expand=1)

        cam_frames = []
        # Setup Tkinter buttons to change OBS scenes and change camera presets.
        for camera in self.cam_sync.cameras:
            cam_frame = Frame(self.main_frame)
            cam_frames.append(cam_frame)
            cam_frame.configure(bg=self.background_color)
            cam_frame.pack(fill="x")
            cam_address = camera.get("address")
            if cam_address is None:
                print("A camera in the config has no address listed!")
            presets = camera.get("presets")
            if presets is None:
                print("Camera at {} has no presets listed!".format(cam_address))
                continue
            cam_id = camera.get("id") or "Unknown"
            cam_label = camera.get("label") or "Camera {}".format(cam_id)
            label = Label(cam_frame, text=cam_label, font=self.font, bg=self.background_color, fg=self.text_color)
            label.pack(padx=5, pady=5, side="left")
            for preset in presets:
                preset_id = preset.get("preset_num")
                scene = preset.get("obs_scene")
                name = preset.get("name") or scene
                if scene in self.cam_sync.obs_scenes:
                    btn = Button(cam_frame, text=name, font=self.font, bg=self.btn_background_color, fg=self.text_color, command=partial(self.cam_sync.change_scene, preset_id, scene, cam_address))
                    btn.pack(padx=5, pady=5, side="left")
                else:
                    print("The scene \"{}\" was not found in your OBS configuration.".format(scene))

        self.master.update()


if __name__ == "__main__":
    # Main window
    root = Tk()

    main_window = MainPTZWindow(root)

    # Start the app
    root.mainloop()
