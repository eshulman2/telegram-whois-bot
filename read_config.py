
import json

def config_parser():
    with open('config.json','r') as config_file:
        config = json.loads(config_file.read())
    return config
