from obswebsocket import obsws, requests


class OBSWebsocketHandler:
    def __init__(self, host, port, password):
        # Setup a websocket connection to OBS
        self.ws = obsws(host, port, password)
        self.ws.connect()
 
        self.scenes = self.get_scenes()

    def get_scenes(self):
        return self.ws.call(requests.GetSceneList()).getScenes()
    
    def change_scene(self, name):
        self.ws.call(requests.SetCurrentScene(name))
