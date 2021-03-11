import json
import os
import sys
import socket
from tkinter import Button, Frame, Label, Menu, Tk, font, messagebox

from obswebsocket import exceptions, obsws, requests

from ptz_visca_commands import PTZViscaCommands

# Changes an internal path variable based on whether the application was built into an EXE or not.
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    __location__ = os.path.dirname(sys.executable)
else:
    __location__ = os.path.realpath(os.path.join(os.getcwd(),
                                    os.path.dirname(__file__)))


def do_exit(message):
    print(message)
    sys.exit()


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
            messagebox.showerror("Error", "OBS Must be open in order to use this application")

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
        
        # The port for camera control
        self.udp_port = 1259
       
    def change_scene(self, preset_num, scene, address):
        """Changes the camera preset and the OBS scene

        Args:
            preset_num (int): The preset number in range: 1-126
            scene (str): OBS Scene name to switch to
            address ([type]): IP Address of the camera to communicate with
        """
        if preset_num > 127 or preset_num < 0:
            messagebox.showerror("Error", "Cannot have a preset number outside range: 1-126!"
                                          "\nScene name: {}, Camera Address: {}".format(scene, address))
        else:
            try:
                # Make a new socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(3)
                # Connect to the camera addres
                sock.connect((address, self.udp_port))
                # Create the bytes to send to change the preset
                preset_hex = repr(chr(preset_num)).strip("'")[2:]
                data = PTZViscaCommands.CAM_Memory_Recall(preset_hex)
                # Send the data and close the socket
                sock.send(data)
                sock.close()
                # Change the OBS Scene
                self.ws_handler.change_scene(scene)
            except socket.error as e:
                messagebox.showerror("Error", "Error sending a camera a preset command!"
                                     "\nAddress: {}, Preset Num: {}. \nSocket Exception: {}".format(address, preset_num, e))
    
    def load_settings(self):
        """ Loads settings into self.settings and collects a list of cameras into self.cameras
        """
        print("Loading settings from disk...")
        with open(os.path.join(__location__, "settings.json"), "r") as f:
            self.settings = json.load(f)
            f.close()
        self.cameras = [camera for camera in self.settings["cameras"]]


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

        # Add a menu bar with a reload option
        menu_bar = Menu(self.master)
        menu_bar.add_command(label="Reload All", command=self.init_window)
        self.master.config(menu=menu_bar)

        # Makes width = 200 if it's less than that
        width = self.master.winfo_width() if self.master.winfo_width() >= 300 else 300
        height = self.master.winfo_height()
        self.master.minsize(width, height)

        self.main_frame = None
        self.init_window()

    def init_window(self):
        if self.main_frame is None:
            # Make main window frame
            self.main_frame = Frame(self.master)
            self.main_frame.configure(bg=self.background_color)
            self.main_frame.pack(fill="both", expand=1)
        else:
            # Main frame exists so we are reloading. Destroy it and recreate it
            self.main_frame.destroy()
            self.cam_sync.load_settings()
            self.main_frame = Frame(self.master)
            self.main_frame.configure(bg=self.background_color)
            self.main_frame.pack(fill="both", expand=1)

        # Setup Tkinter buttons to change OBS scenes and change camera presets.
        for camera in self.cam_sync.cameras:
            cam_address = camera.get("address")
            cam_id = camera.get("id") or "Unknown"
            if cam_address is None:
                messagebox.showinfo("Info", "A camera in the config has no address listed!"
                                    "\nCamera ID: {}".format(cam_id))
                continue
            presets = camera.get("presets")
            if presets is None:
                messagebox.showinfo("Info", "Camera at {} has no presets listed!".format(cam_address))
                continue
            cam_label = camera.get("label") or "Camera {}".format(cam_id)
            cam_frame = Frame(self.main_frame)
            cam_frame.configure(bg=self.background_color)
            cam_frame.pack(fill="x")
            label = Label(cam_frame, text=cam_label, font=self.font, bg=self.background_color, fg=self.text_color)
            label.pack(padx=5, pady=5, side="left")
            for preset in presets:
                preset_id = preset.get("preset_num")
                scene = preset.get("obs_scene")
                name = preset.get("name") or scene
                if scene in self.cam_sync.obs_scenes:
                    btn = Button(cam_frame, text=name, font=self.font, bg=self.btn_background_color, fg=self.text_color, command=lambda: self.cam_sync.change_scene(preset_id, scene, cam_address))
                    btn.pack(padx=5, pady=5, side="left")
                else:
                    messagebox.showinfo("Info", "The scene \"{}\" was not found in your OBS configuration."
                                        "\nCamera ID: {}".format(scene, cam_id))

        self.master.update()


if __name__ == "__main__":
    # Main window
    root = Tk()

    main_window = MainPTZWindow(root)

    # Start the app
    root.mainloop()
