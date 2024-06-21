import yaml.loader

class Type:

    TRACK = 'TRACK'
    ALBUM = 'ALBUM'
    PLAYLIST = 'PLAYLIST'

class YamlFile:
    def __init__(self, path):
        with open(path) as file:
            config_data = yaml.safe_load(file)
        self.__dict__.update(config_data) # auto assign of fields to keep constructor clean