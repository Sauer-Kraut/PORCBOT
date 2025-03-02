import discord
from discord.ext import tasks, commands
import SecurityModule
import config as Config
import StorageModule as Storage
import ServerCommunicationModule as API
from colorama import Fore, Style
import json
import os

from DailogeModule import DialoguePlan, DialogueData, DialogueStep, LeapData

bot = Config.bot


async def completion_script_0():
    async def evaluator(dialogue_data, approval):
        # print("completion script 0 executing")
        if approval:
            await Storage.store_user(Config.remaining_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(Config.contacted_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(Config.declined_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)

            result = await API.sign_up_user(user=Config.bot.get_user(dialogue_data.user_id), bp="NaN", region="NaN")

            if result is None:
                return [1, dialogue_data]

            elif "Similar Sign Up already exists" in result:
                dialogue_data.data.sign_up_error = result
                return [1, dialogue_data]

            else:
                dialogue_data.data.sign_up_error = result
                return [3, dialogue_data]

        else:
            await Storage.store_user(Config.declined_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(Config.contacted_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(Config.remaining_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            return [2, dialogue_data]

    return evaluator

async def message_script_0():
    async def constructor(dialogue_data):
        message = f'''
Hello, I'm PORC bot, the new hire of the PORC organization team.
As of now you are an active member of the second season of the PORC league which will end December 6th.
If you want to **continue being a part of part of PORC for the third season please react to with** ✅ to this message.
If you react with ❌ or do not react to this message you will **not be entered** into the third season of PORC.
**Declining this message will take priority** over singups via other route like our website.
Thanks for participating and we hope you enjoy your time with PORC.

**Do you want to participate in the third season of PORC?**
        '''.strip()
        return message

    return constructor


async def message_script_1():
    async def constructor(dialogue_data):
        message = f'''Signup completed'''.strip()
        return message

    return constructor


async def message_script_2():
    async def constructor(dialogue_data):
        message = f'''Your decline was registered successfully. In case you change your mind you can sign up via our website at https://porc.mywire.org/signup'''.strip()
        return message

    return constructor


async def message_script_3():
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


async def construct(user_id, role, index):
    data = LeapData(role=role, sign_up_error=None)

    dialogue_data = \
        DialogueData(
            "SeasonLeap",
            user_id,
            data
        )

    return DialoguePlan(
        index,
        dialogue_data,
        [
            DialogueStep(
                await message_script_0(), # would you like to sign up?
                "react",
                await completion_script_0()
            ),
            DialogueStep(
                await message_script_1(), # sign up complete
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_2(), # decline registered successfully
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_3(), # error occurred
                "info",
                await completion_script_end()
            )
        ]
    )
