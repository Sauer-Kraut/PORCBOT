import discord
from discord.ext import tasks, commands
from dataclasses import dataclass, asdict
import asyncio
import DailogeModule
import SecurityModule
import json
import os
import threading
import config as Config

securityModule = SecurityModule.SecurityModule()


async def store_user(list_name, User, data):
    # [username, data(BP), id]
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    double_check = True

    # User Data gets serialized (turned into a string), encrypted (turned into bytes and manipulated), and finally decoded (turned into text),
    # so that it can then be written to the json file
    user_data = [User.name, data, User.id]
    encrypted_user_data = securityModule.encrypt(user_data)
    for entry in user_list:
        decrypted_entry = securityModule.decrypt(entry)

        if user_data == decrypted_entry:
            double_check = False

    if double_check:
        user_list.append(encrypted_user_data)

    with open(list_name, "w") as file:
        json.dump(user_list, file, indent=4)



async def read_list(list_name):
    # [username, data(BP), id]
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    # User Data gets encoded (turned into bytes), decrypted (turned into bytes and manipulated), and finally deserialized (turned into a list),
    # so that it can then be read
    decrypted_list = []
    for entry in user_list:
        decrypted_list.append(securityModule.decrypt(entry))

    return decrypted_list


# @bot.command()
async def remove_user(list_name, User, data):
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    user_data = [User.name, data, User.id]
    for index, entry in enumerate(user_list):
        decrypted_entry = securityModule.decrypt(entry)

        if user_data == decrypted_entry:
            del user_list[index]

    with open(list_name, "w") as file:
        json.dump(user_list, file)




async def read_list_no_id(list_name):
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    # User Data gets encoded (turned into bytes), decrypted (turned into bytes and manipulated), and finally deserialized (turned into a list),
    # so that it can then be read
    decrypted_list = []
    for entry in user_list:
        decrypted_entry = securityModule.decrypt(entry)
        parsed_entry = [decrypted_entry[0], decrypted_entry[1]]
        decrypted_list.append(parsed_entry)

    return decrypted_list


dialogue_lock = False

async def get_dialogue_lock():
    # print("getting lock")
    global dialogue_lock
    while dialogue_lock is True:
        await asyncio.sleep(0.1)
    dialogue_lock = True

async def drop_dialogue_lock():
    # print("dropping lock")
    global dialogue_lock
    dialogue_lock = False

async def store_dialogue_builders(list_name, dialogue_builders):
    # print("storing")

    with open(list_name, "r") as file:
        try:
            builder_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            builder_list = []

    with open(list_name, "w") as file:
        json.dump([d.serialize() for d in dialogue_builders], file, indent=4)

    await drop_dialogue_lock()



async def read_dialogue_builders(list_name):
    # print("reading")
    await get_dialogue_lock()

    with open(list_name, "r") as file:
        try:
            builder_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            builder_list = []

    deserialized_list = [DailogeModule.DialogueBuilder.deserialize(d) for d in builder_list]

    return deserialized_list



FILE_LOCK = threading.Lock()
def write_request_to_file(data):
    """Append request data to the JSON file."""
    with FILE_LOCK:
        try:
            with open(Config.REQUESTS_FILE, "r+", encoding="utf-8") as f:
                requests = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            requests = []

        requests.append(data)  # Add new request

        with open(Config.REQUESTS_FILE, "w", encoding="utf-8") as f:
            json.dump(requests, f, indent=4)



# TODO: Add a check for user function
