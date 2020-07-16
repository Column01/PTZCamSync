# PTZCamSync
A simple application that will (hopefully) allow users to manage PTZ Optics cameras and OBS scene switching with a simple click of a button

# Setup
Clone the repository to a folder you'd like to use for the program

### Setup Python Environment

1. Install Python 3.6+ 64bit
2. Create a python venv called "PTZCamSync" and run the provided `activate.ps1` script to activate it.
3. Run: `pip install -r requirements.txt` in this new command prompt to install all dependencies

### Configure OBS

1. Install the OBS Websocket program from [here](https://github.com/Palakis/obs-websocket) and configure it
2. Create your scenes you wish to use and note their names down somewhere

### Configure PTZ Optics Camera
Follow your user manual on how to configure your PTZ Optics Camera and set presets. Make sure you note down the preset numbers for use later in configuring the program

### Configure the program

See the [configuration guide](CONFIGURATION.md) where it shows you how to configure your settings for the program

