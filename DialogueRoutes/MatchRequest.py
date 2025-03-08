import discord
from discord.ext import tasks, commands
import SecurityModule
import config as Config
import StorageModule as Storage
import ServerCommunicationModule as API
import DiscordModule as Communication
from colorama import Fore, Style
import json
import os

from DailogeModule import DialoguePlan, DialogueData, DialogueStep, LeapData, InviteData, MatchRequestData

bot = Config.bot


async def completion_script_0():
    async def evaluator(dialogue_data, approval: bool, no_resp: bool):
        # print("completion script 0 executing")
        if no_resp:
            higher_id = int(dialogue_data.data.challenger_id)
            lower_id = int(dialogue_data.data.opponent_id)

            if lower_id > higher_id:
                higher_id = lower_id
                lower_id = int(dialogue_data.data.challenger_id)

            match_id = f"{lower_id}V{higher_id}@{int(dialogue_data.data.start_timestamp)}"

            status = await API.get_match_status(match_id=match_id)

            if status == "Confirmed":
                return [4, dialogue_data]

            elif status == "Declined":
                return [5, dialogue_data]

            else:
                return [-1, dialogue_data]

        elif approval:

            error = await API.update_match_status(start_timestamp=dialogue_data.data.start_timestamp,
                                                  challenger_id=dialogue_data.data.challenger_id,
                                                  opponent_id=dialogue_data.data.opponent_id,
                                                  status="Confirmed")

            if error is None:

                event = await Communication.create_match_event(start_timestamp=dialogue_data.data.start_timestamp,
                                                               challenger_username=Config.bot.get_user(dialogue_data.data.challenger_id).display_name,
                                                               opponent_username=Config.bot.get_user(dialogue_data.data.opponent_id).display_name,
                                                               league=dialogue_data.data.league)

                dialogue_data.data.event_id = event.id

                event_link = f"https://discord.com/events/{Config.porc_guild_id}/{event.id}"
                await Communication.send_info_message(user_target=Config.bot.get_user(dialogue_data.data.challenger_id),
                                                      content=f'''Your requested match with {Config.bot.get_user(dialogue_data.data.opponent_id).display_name} has been accepted:
{event_link}''')

                return [1, dialogue_data]

            else:
                return [3, dialogue_data]

        else:

            error = await API.update_match_status(start_timestamp=dialogue_data.data.start_timestamp,
                                                  challenger_id=dialogue_data.data.challenger_id,
                                                  opponent_id=dialogue_data.data.opponent_id,
                                                  status="Declined")

            if error is None:
                return [2, dialogue_data]

            else:
                return [3, dialogue_data]

    return evaluator


async def message_script_0():
    async def constructor(dialogue_data):
        challenger = Config.bot.get_user(dialogue_data.data.challenger_id).display_name
        message = f'''
**{challenger} has requested a match with you on <t:{dialogue_data.data.start_timestamp}:F>**. 
You can accept his proposal via reacting with {Config.accept_emoji} or decline with {Config.decline_emoji}.
        '''.strip()
        return message

    return constructor


async def message_script_1():
    async def constructor(dialogue_data):
        event_link = f"https://discord.com/events/{Config.porc_guild_id}/{dialogue_data.data.event_id}"
        message = f'''Your match has been registered successfully. An event has been created on the PORC discord server ^^: {event_link}'''.strip()
        return message

    return constructor


async def message_script_2():
    async def constructor(dialogue_data):
        message = f'''Your decline was registered successfully. 
You can find all your opponents schedules as well as make offers yourself over on the [porc website](https://porc.mywire.org)'''.strip()
        return message

    return constructor



async def message_script_3():
    async def constructor(dialogue_data):
        message = f'''Something went wrong while updating the match status. Feel free to contact the PORC mods about this and sorry for the inconvenience. 
You can try to accept/decline the request over the [porc website](https://porc.mywire.org) instead'''.strip()
        return message

    return constructor



async def message_script_4():
    async def constructor(dialogue_data):
        message = f'''Your approval via the website has been registered.'''.strip()
        return message

    return constructor



async def completion_script_4():
    async def responder(dialogue_data):
        # print("completion script end executing")
        error = await API.update_match_status(start_timestamp=dialogue_data.data.start_timestamp,
                                              challenger_id=dialogue_data.data.challenger_id,
                                              opponent_id=dialogue_data.data.opponent_id,
                                              status="Confirmed")

        if error is None:

            print(f"challenger id: {dialogue_data.data.challenger_id}, opponent id: {dialogue_data.data.opponent_id}")

            event = await Communication.create_match_event(start_timestamp=dialogue_data.data.start_timestamp,
                                                           challenger_username=Config.bot.get_user(dialogue_data.data.challenger_id).display_name,
                                                           opponent_username=Config.bot.get_user(dialogue_data.data.opponent_id).display_name,
                                                           league=dialogue_data.data.league)

            dialogue_data.data.event_id = event.id

            event_link = f"https://discord.com/events/{Config.porc_guild_id}/{event.id}"
            await Communication.send_info_message(user_target=Config.bot.get_user(dialogue_data.data.challenger_id),
                                                  content=f'''Your requested match with {Config.bot.get_user(dialogue_data.data.opponent_id).display_name} has been accepted:
        {event_link}''')

            return [1, dialogue_data]

        else:
            return [3, dialogue_data]

    return responder



async def message_script_5():
    async def constructor(dialogue_data):
        message = f'''Your decline via the website has been registered.'''.strip()
        return message

    return constructor


async def completion_script_end():
    async def responder(dialogue_data):
        # print("completion script end executing")
        return [600, dialogue_data]

    return responder


async def construct(dialogue_data, index):

    return DialoguePlan(
        index,
        dialogue_data,
        [
            DialogueStep(
                await message_script_0(),  # _____ requested a match with you at _____, do you agree?
                "react",
                await completion_script_0()
            ),
            DialogueStep(
                await message_script_1(),  # Your match has been registered successfully: __link__
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_2(),  # your decline has been registered successfully
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_3(),  # failed to do API call
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_4(),  # Your approval via the website has been registered -> 1
                "info",
                await completion_script_4()
            ),
            DialogueStep(
                await message_script_5(),  # Your decline via the website has been registered
                "info",
                await completion_script_end()
            )
        ]
    )
