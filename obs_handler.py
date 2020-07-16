from obswebsocket import obsws, requests


class OBSWebsocketHandler:
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
