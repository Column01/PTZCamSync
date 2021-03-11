class PTZViscaCommands:
    # Potential Future commands
    CAM_Power_On = "8101040002FF"
    CAM_Power_Off = "8101040003FF"

    @classmethod
    def CAM_Memory_Recall(preset_hex):
        return bytes.fromhex("8101043F02{preset_num_hex}FF".format(preset_num_hex=preset_hex))

    @classmethod
    def CAM_Memory_Reset(preset_hex):
        return bytes.fromhex("8101043F00{preset_num_hex}FF".format(preset_num_hex=preset_hex))

    @classmethod
    def CAM_Memory_Set(preset_hex):
        return bytes.fromhex("8101043F01{preset_num_hex}FF".format(preset_num_hex=preset_hex))
