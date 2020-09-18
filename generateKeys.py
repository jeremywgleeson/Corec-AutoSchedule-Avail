import random
import string
import json
import os

KEYS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "project", "keys_file.json")

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def write_data(keys_data):
    """ write keys_data to file """
    with open(KEYS_FILE, "w") as f:
        json.dump(keys_data, f, indent=2)

def create_keys(num, length):
    """ generate num of unique keys and return them in a list """
    existing_keys = None

    # get list of all keys previously generated
    try:
        with open(KEYS_FILE, "r") as f:
            keys_data = json.load(f)
            existing_keys = keys_data["valid_keys"]
            for val in keys_data["used_keys"]:
                existing_keys.append(val["key"])
    except IOError:
        existing_keys = []

    # generate unqiue keys
    out_keys_list = []
    for i in range(0, num):
        new_key = get_random_alphanumeric_string(length)
        while new_key in existing_keys:
            new_key = get_random_alphanumeric_string(length)
        out_keys_list.append(new_key)

    return out_keys_list

def add_keys(num):
    """ generate num of unique keys and add them to valid_keys """
    try:
        with open(KEYS_FILE, "r") as f:
            keys_data = json.load(f)
    except IOError:
        # if not exists, init empty file
        keys_data = {"valid_keys": []}

    for new_key in create_keys(num, 13):
        keys_data["valid_keys"].append(new_key)
        print(new_key)

    write_data(keys_data)

def main():
    print("Used to generate user keys for Corec AutoScheduler")
    num = input("How many keys would you like to add?\n: ")
    print()
    while not num.isdigit():
        print("Please enter a valid number!")
        num = input("How many keys would you like to add?\n: ")

    add_keys(int(num))

if __name__ == "__main__":
    main()
