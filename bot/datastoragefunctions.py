import json

def dataStorageRead():
    """
    Simple data_storage.json read (example of data_storage.json in README)
    """
    with open(f"bot/data_storage.json", "r") as file:
        return json.load(file)
    
def dataStorageWrite(data):
    """
    Data storage writer, accepts only a whole data file, please do not send partial data
    """
    with open(f"bot/data_storage.json", "w") as file:
        json.dump(data, file)