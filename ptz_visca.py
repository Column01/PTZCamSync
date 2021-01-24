import socket


class PTZCommands:
    # Potential Future commands
    CAM_Power_On = "8101040002FF"
    CAM_Power_Off = "8101040003FF"
    CAM_Memory_Reset = "8101043F00{preset_num_hex}FF"
    CAM_Memory_Set = "8101043F01{preset_num_hex}FF"

    # Camera recall preset command
    CAM_Memory_Recall = "8101043F02{preset_num_hex}FF"

    # Completion messages (NOT SURE IF THIS CHANGES FOR EVERYONE! IT PERSISTED ACROSS RESTARTS!)
    CAM_Completion_Q = b'\x90Q\xff'
    CAM_Completion_R = b'\x90R\xff'

class PTZViscaSocket:
    """An instance of a PTZ visca socket connection
    """
    def __init__(self, address):
        self.address = address
        self.port = 5678
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.socket.settimeout(10)
        try:
            print("Trying to connect to: {}".format(self.address))
            self.socket.connect((self.address, self.port))
            self.is_connected = True
            print("Connected successfully!")
        except socket.error as e:
            print("Error connecting to socket on address: {}.\nException: {}".format(address, e))
            self.is_connected = False

    def is_my_socket(self, address):
        return address == self.address

    def change_preset(self, preset_num):
        """Changes the camera's current position preset

        Args:
            preset_num (int): The preset to change to (0-127)
        """
        if preset_num > 127 or preset_num < 0:
            print("Invalid preset number!")
            return False
        preset_hex = repr(chr(preset_num)).strip("'")[2:]
        data = bytes.fromhex(PTZCommands.CAM_Memory_Recall.format(preset_num_hex=preset_hex))
        try:
            self.socket.send(data)
        except socket.error as e:
            print("Error sending command to socket on address: {}.\nException: {}".format(self.address, e))
            self.is_connected = False
            return False

        total_data = []
        flag = False
        while not flag:
            total_data.append(self.socket.recv(1024))
            if PTZCommands.CAM_Completion_Q in total_data or PTZCommands.CAM_Completion_R in total_data:
                total_data.clear()
                flag = True
                return True

        return False

    def close(self):
        print("Disconnecting from: {}".format(self.address))
        self.socket.close()
