import socket
from tkinter import messagebox


class PTZCommands:
    # Potential Future commands
    CAM_Power_On = "8101040002FF"
    CAM_Power_Off = "8101040003FF"
    CAM_Memory_Reset = "8101043F00{preset_num_hex}FF"
    CAM_Memory_Set = "8101043F01{preset_num_hex}FF"

    # Camera recall preset command
    CAM_Memory_Recall = "8101043F02{preset_num_hex}FF"


class PTZViscaSocket:
    """An instance of a PTZ visca socket connection
    """
    def __init__(self, address):
        self.address = address
        self.port = 5678
        self.socket = None
        self.is_connected = False
        self.connect()
        if not self.is_connected:
            messagebox.showinfo("Info", "Unable to connect to camera at adddress: {}".format(self.address))

    def is_my_socket(self, address):
        return address == self.address

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.socket.settimeout(3)
            print("Trying to connect to: {}".format(self.address))
            self.socket.connect((self.address, self.port))
            self.is_connected = True
            print("Connected successfully!")
            return
        except socket.error as e:
            print("Error connecting to socket on address: {}.\nException: {}".format(self.address, e))
            self.is_connected = False

    def change_preset(self, preset_num):
        """Changes the camera's current position preset

        Args:
            preset_num (int): The preset to change to (0-127)
        """
        if preset_num > 127 or preset_num < 0:
            print("Invalid preset number!")
            return False, "Invalid preset number: {}".format(preset_num)
        preset_hex = repr(chr(preset_num)).strip("'")[2:]
        data = bytes.fromhex(PTZCommands.CAM_Memory_Recall.format(preset_num_hex=preset_hex))
        try:
            if not self.is_connected:
                self.connect()
            if self.is_connected:
                self.socket.send(data)
                return True, ""
            else:
                return False, "Error connecting to Camera"
        except socket.error as e:
            print("Error sending command to socket on address: {}.\nException: {}".format(self.address, e))
            self.is_connected = False
            return False, e

    def close(self):
        print("Disconnecting from: {}".format(self.address))
        self.socket.close()
