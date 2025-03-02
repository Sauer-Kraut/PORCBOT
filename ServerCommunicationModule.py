import discord
from discord.ext import tasks, commands
import SecurityModule
import StorageModule as Storage
from colorama import Fore, Style
import os
import requests
import re
import time


def sanitize_input(input_str):
    # Remove everything except digits and the letter 'k'
    sanitized_str = ''.join([char for char in input_str if char.isdigit() or char.lower() == 'k'])

    # Find any numbers followed directly by 'k' and add 3 zeros
    match = re.search(r'(\d+)(k)', sanitized_str)
    if match:
        number = match.group(1)
        # Append three zeros to the number
        sanitized_str = sanitized_str.replace(match.group(), f"{number}000")

    # Remove 'k' and keep only digits
    sanitized_str = ''.join([char for char in sanitized_str if char.isdigit()])

    # If there are no digits, return "0"
    return sanitized_str if sanitized_str else "0"


async def sign_up_user(user, bp, region):

    print(f"\nSigning up user {user.name} via API")

    target_url = "https://porc.mywire.org/api/sign-up"

    payload = {
        "title": "Discord Bot sign up",
        "sing_up_info": {   # misspelled, but so is it in the backend
            "username": f"{user.name}",
            "bp": int(sanitize_input(f"{bp}")),
            "region": f"{region}",
            "discord_id": f"{user.id}",
            "date": f"{int(time.time())}"
        }
    }

    response = requests.post(target_url, json=payload)

    if response.status_code == 200:

        data = response.json()
        error = data['error']

        if error is None:
            print(Fore.GREEN + Style.NORMAL + "Sing up POST request successful!")

        else:
            print(Fore.YELLOW + Style.NORMAL + f"API call failed with error message {error}.")

        return error

    else:
        print(Fore.RED + Style.NORMAL + f"API call failed with status code {response.status_code}.")
        return f"API call failed with status code {response.status_code}."


async def remove_sign_up_user(user):

    print(f"\nRemoving sign up of user {user.name} via API")

    target_url = "https://porc.mywire.org/api/sign-up/remove"

    payload = {
        "title": "Discord Bot sign up removal",
        "sing_up_info": {  # misspelled, but so is it in the backend
            "username": f"{user.name}",
            "bp": 0,
            "region": f"",
            "discord_id": f"{user.id}"
        }
    }

    response = requests.post(target_url, json=payload)

    if response.status_code == 200:

        data = response.json()
        error = data['error']

        if f"{error}" == "None":
            print(Fore.GREEN + Style.NORMAL + "Sing up removal POST request successful!")

        else:
            print(Fore.YELLOW + Style.NORMAL + f"API call failed with error message {error}.")

    else:
        print(Fore.RED + Style.NORMAL + f"API call failed with status code {response.status_code}.")




async def get_signed_up_ids():

    print("\nMaking GET request for the sign ups :3")

    target_url = "https://porc.mywire.org/api/sign-up"

    response = requests.get(target_url)

    if response.status_code == 200:

        data = response.json()
        error = data['error']

        if f"{error}" == "None":
            print(Fore.GREEN + Style.NORMAL + "Sing ups GET request successful!")

            signups = data['data']
            userids = [id['discord_id'] for id in signups]

            return userids

        else:
            print(Fore.RED + Style.NORMAL + f"API call failed with error message {error}.")


    else:
        print(Fore.RED + Style.NORMAL + f"API call failed with status code {response.status_code}.")




async def get_plan_blueprint():

    print("I will give you a blueprint OwO")

    print("\nMaking GET request for plan blueprint :3")

    target_url = "https://porc.mywire.org/api/plan-blueprint"

    response = requests.get(target_url)

    if response.status_code == 200:

        data = response.json()
        error = data['error']

        if f"{error}" == "None":
            print(Fore.GREEN + Style.NORMAL + "Sing ups GET request successful!")

            blueprint = data['data']

            return blueprint

        else:
            print(Fore.RED + Style.NORMAL + f"API call failed with error message {error}.")


    else:
        print(Fore.RED + Style.NORMAL + f"API call failed with status code {response.status_code}.")



async def post_plan_blueprint(plan):

    print("I will try to start a new season -w-")

    print(Fore.MAGENTA + Style.BRIGHT + f"\nMaking a POST request for a Plan Blueprint via API")

    target_url = "http://porc.mywire.org/api/season-control"

    payload = {
        "title": "Discord Bot plan blueprint POST",
        "plan": plan
    }

    response = requests.post(target_url, json=payload)

    if response.status_code == 200:

        data = response.json()
        error = data['error']

        if f"{error}" == "None":
            print(Fore.GREEN + Style.BRIGHT + "Plan Blueprint POST request successful!")
            return "None"

        else:
            print(Fore.YELLOW + Style.NORMAL + f"API call failed with error message {error}.")
            return f"{error}"

    else:
        print(Fore.RED + Style.NORMAL + f"API call failed with status code {response.status_code}.")