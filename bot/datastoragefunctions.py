import json
import os

DSF_PATH = os.path.join(os.path.dirname(__file__))
DATA_STORAGE = os.path.join(DSF_PATH, "data_storage.json")
USER_STORAGE = os.path.join(DSF_PATH, "user_storage.json")

def dataStorageRead():
    """
    Simple data_storage.json read (example of data_storage.json in README)
    """
    with open(DATA_STORAGE, "r") as file:
        return json.load(file)
    
def dataStorageWrite(data):
    """
    Data storage writer, accepts only a whole data file, please do not send partial data
    """
    with open(DATA_STORAGE, "w") as file:
        json.dump(data, file, indent=4)

def userStorage(wr, user, data = None):
    """
    All in one user_storage.json reader
    """
    with open(USER_STORAGE, "r") as file:
        all_users = json.load(file)
    if wr == "r":
        try:
            return all_users[str(user)]
        except:
            return all_users["default"]
    elif wr == "w":
        with open(USER_STORAGE, "w") as file:
            all_users[str(user)] = data
            json.dump(all_users, file, indent=4)
