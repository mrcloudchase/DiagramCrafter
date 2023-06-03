import json

def load_config(filename):
    with open(filename) as config_file:
        data = json.load(config_file)
    # Perform any necessary validation on the data here.
    return data
