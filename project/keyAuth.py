import json
import os
from datetime import datetime

KEYS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keys_file.json")

def check_key(key):
    try:
        with open(KEYS_FILE, "r") as f:
            keys_data = json.load(f)
            if "valid_keys" in keys_data:
                if keys_data["valid_keys"]:
                    if key in keys_data["valid_keys"]:
                        return None
            if "used_keys" in keys_data:
                if keys_data["used_keys"]:
                    for key_data in keys_data["used_keys"]:
                        if key_data["key"] == key:
                            return "Key already used."
    except IOError:
        return "Invalid key."
    return "Invalid key."

def use_key(key, username):
    # make sure its unused
    if not check_key(key):
        try:
            keys_data = None
            with open(KEYS_FILE, "r") as f:
                keys_data = json.load(f)
                if "used_keys" not in keys_data:
                    keys_data["used_keys"] = []
                new_used = {"key": key,
                            "used_by": username,
                            "time": datetime.now().strftime("%m/%d/%Y %H:%M:%S")}
                keys_data["used_keys"].append(new_used)
                keys_data["valid_keys"].remove(key)
            with open(KEYS_FILE, "w") as f:
                json.dump(keys_data, f, indent=2)
            return True
        except IOError:
            return False
    return False
