# Configuring the application

All changes are made in the included `settings.json` file.
If you downloaded the repo directly, there is an example config at the end you can copy and create the file manually.

Inside it you will need to copy the text at the bottom of this page and paste it. You will need to change values as needed. Use a JSON linter to verify you didn't mess it up.

## Adding a camera

Create a new JSON object in the `cameras` section of the file with the following information:

- `id`
  - Arbitrary numbering scheme of the cameras that must be unique
- `address`
  -The camera's IP address on your local network to send it requests
- `presets` (json array)
  - `name`
    - The display name for the preset
  - `preset_num`
    - The camera's preset number you want to use for this preset. This should have restrictions for what it can be. Check your camera's manual for details
  - `obs_scene`
    - The name of the OBS scene you want this preset to correspond to

## Config example

    {   
      "password": "$tr0ng_pa$$w0rd",
      "cameras": [
        {   
          "id": 1,
          "address": "192.168.1.88",
          "label": "Label for this camera"
          "presets": [
            {"name": "Preset Name", "preset_num": 1, "obs_scene": "Example Scene Name"},
            {"name": "Preset Name 2", "preset_num": 2, "obs_scene": "Example Scene Name 2"}
          ]
        }
      ]
    }
