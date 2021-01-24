# PTZCamSync

A simple application that allows users to manage [PTZ Optics](https://ptzoptics.com/) cameras and [OBS Studio](https://obsproject.com/) scene switching with a simple click of a button

## Setup

### Note

You can skip the python setup section by downloading the latest release of the program [here](https://github.com/Column01/PTZCamSync/releases)

If you'd like to play with the source directly, clone the repository to a folder you'd like to use for the program and follow along with all steps below.

### Setup Python Environment

1. Install Python 3.6+ 64bit
2. Create a python venv called "PTZCamSync" and activate it.
3. Run: `pip install -r requirements.txt` in this new command prompt to install all dependencies

### Configure OBS

1. Install the OBS Websocket program from [here](https://github.com/Palakis/obs-websocket) and configure it
2. Create your scenes you wish to use and note their names down somewhere

### Configure PTZ Optics Camera

Follow your user manual on how to configure your PTZ Optics Camera and set presets. Make sure you note down the preset numbers for use later in configuring the program

### Configure the program

See the [configuration guide](CONFIGURATION.md) where it shows you how to configure your settings for the program
