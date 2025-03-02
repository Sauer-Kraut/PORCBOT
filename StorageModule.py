import discord
from discord.ext import tasks, commands
from dataclasses import dataclass, asdict

import DailogeModule
import SecurityModule
import json
import os

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



async def store_dialogue_builders(list_name, dialogue_builders):

    with open(list_name, "r") as file:
        try:
            builder_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            builder_list = []

    with open(list_name, "w") as file:
        json.dump([d.serialize() for d in dialogue_builders], file, indent=4)



async def read_dialogue_builders(list_name):

    with open(list_name, "r") as file:
        try:
            builder_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            builder_list = []

    deserialized_list = [DailogeModule.DialogueBuilder.deserialize(d) for d in builder_list]

    return deserialized_list



# TODO: Add a check for user function
