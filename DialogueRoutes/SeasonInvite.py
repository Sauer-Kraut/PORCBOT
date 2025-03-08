import discord
from discord.ext import tasks, commands
import SecurityModule
import config as Config
import StorageModule as Storage
import ServerCommunicationModule as API
from colorama import Fore, Style
import json
import os

from DailogeModule import DialoguePlan, DialogueData, DialogueStep, LeapData, InviteData

bot = Config.bot


async def completion_script_0():
    async def evaluator(dialogue_data, approval: bool, no_resp: bool):
        # print("completion script 0 executing")
        if no_resp:
            return [-1, dialogue_data]

        elif approval:
            await Storage.store_user(Config.pending_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.declined_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.confirmed_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.contacted_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            return [1, dialogue_data]

        else:
            await Storage.store_user(Config.declined_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.pending_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.confirmed_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.contacted_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            return [2, dialogue_data]

    return evaluator


async def message_script_0():
    async def constructor(dialogue_data):
        iteration = "fifth"
        season_start = "1741460400"
        message = f'''
Hello, I'm PORC bot, the organizer bot of PORC.
You are receiving this message because you currently have the competitor role but are not competing in the PORC league.
If you want to **sign up for the {iteration} season of PORC**, which will start **<t:{season_start}:F>**, please react with ✅ to this message.
If you react with ❌ or do not react, you will **not be entered** into the {iteration} season of PORC.

**Do you want to participate in the {iteration} season of PORC?**
        '''.strip()
        return message

    return constructor


async def completion_script_1():
    async def responder(dialogue_data, response):
        # print("completion script end executing")
        dialogue_data.data.bp = response

        result = await API.sign_up_user(user=Config.bot.get_user(dialogue_data.user_id), bp=response, region="NaN")
        dialogue_data.data.sign_up_error = result

        if result is None or "Similar Sign Up already exists" in result:
            await Storage.store_user(Config.confirmed_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.declined_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.pending_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            await Storage.remove_user(Config.contacted_invite_file_name, bot.get_user(dialogue_data.user_id), "NaN")
            return [3, dialogue_data]

        else:
            return [4, dialogue_data]

    return responder

async def message_script_1():
    async def constructor(dialogue_data):
        message = f'''What is your BP?'''.strip()
        return message

    return constructor


async def message_script_2():
    async def constructor(dialogue_data):
        message = f'''Your decline was registered successfully. In case you change your mind you can sign up via our website at https://porc.mywire.org/signup'''.strip()
        return message

    return constructor


async def message_script_3():
    async def constructor(dialogue_data):
        message = f'''Signup completed'''.strip()
        return message

    return constructor


async def message_script_4():
    async def constructor(dialogue_data):
        message = f'''An error occurred during the signup process: {dialogue_data.data.sign_up_error}
If you do not understand why you received this error we recommend you try to sign up via the website or contact on of our mods on the PORC server'''.strip()
        return message

    return constructor


async def completion_script_end():
    async def responder(dialogue_data):
        # print("completion script end executing")
        return [600, dialogue_data]

    return responder


async def construct(dialogue_data, index: int):

    return DialoguePlan(
        index,
        dialogue_data,
        [
            DialogueStep(
                await message_script_0(),  # would you like to sign up?
                "react",
                await completion_script_0()
            ),
            DialogueStep(
                await message_script_1(),  # whats your BP?
                "response",
                await completion_script_1()
            ),
            DialogueStep(
                await message_script_2(),  # your decline was registered
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_3(),  # sign up successful
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_4(),  # error occurred
                "info",
                await completion_script_end()
            )
        ]
    )
