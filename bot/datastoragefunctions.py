import json

def dataStorageRead():
    """
    Simple data_storage.json read (example of data_storage.json in README)
    """
    with open("bot/data_storage.json", "r") as file:
        return json.load(file)
    
def dataStorageWrite(data):
    """
    Data storage writer, accepts only a whole data file, please do not send partial data
    """
    with open("bot/data_storage.json", "w") as file:
        json.dump(data, file)

def userStorage(wr, user, data = None):
    """
    All in one user_storage.json reader
    """
    with open("bot/user_storage.json", "r") as file:
        all_users = json.load(file)
    if wr == "r":
        try:
            return all_users[str(user)]
        except:
            return all_users["default"]
    elif wr == "w":
        with open("bot/user_storage.json", "w") as file:
            all_users[str(user)] = data
            json.dump(all_users, file)
