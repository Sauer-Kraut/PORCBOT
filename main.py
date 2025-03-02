import discord
from discord.ext import tasks, commands
import SecurityModule
import config as Config
import DailogeModule as Dialogue
import StorageModule as Storage
import DiscordModule as Communication
import ServerCommunicationModule as API
from colorama import Fore, Style
import json
import os

from DialogueRoutes.SeasonLeap import LeapData

# Setup security module for encryption and decryption
securityModule = SecurityModule.SecurityModule()

bot = Config.bot

token = os.getenv("PORC_TOKEN")


@tasks.loop(minutes=3)
async def dialogue_checker_loop():

    print(Fore.RESET + Style.NORMAL + "Checking up on running conversations OwO")

    dialogue_builders = await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json")
    updated_dialogues = []

    for dialogue_builder in dialogue_builders:

        dialogue = await dialogue_builder.build()
        username = Config.bot.get_user(dialogue.dialogue_data.user_id).name
        print(Fore.RESET + Style.NORMAL + f"\nchecking dialogue of type: " + Fore.RESET + Style.BRIGHT + f"{dialogue.dialogue_data.kind}" + Fore.RESET + Style.NORMAL + " with user: " + Fore.RESET + Style.BRIGHT + f"{username}")
        await dialogue.check()

        if dialogue.index != 600:

            updated_dialogues.append(dialogue.getBuilder())

        else:

            print(Fore.RESET + Style.NORMAL + f"Finished a dialogue")

    await Storage.store_dialogue_builders(list_name="Dialogues/Dialogues.json", dialogue_builders=updated_dialogues)


# Event: when the bot is ready
@bot.event
async def on_ready():
    print(Fore.RESET + Style.BRIGHT + f"{bot.user} is now online! OwO")
    dialogue_checker_loop.start()


@bot.event
async def on_reaction_add(reaction, user):
    if user.id != bot.user.id:
        try:
            dialogue_checker_loop.restart()

        except:
            print(Fore.RED + Style.NORMAL + "\ncouldn't restart a loop\n")


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id:

        # checks if message is dm
        if isinstance(message.channel, discord.DMChannel):
            try:
                dialogue_checker_loop.restart()
            except:
                print(Fore.RED + Style.NORMAL + "\ncouldn't restart a loop\n")

        await bot.process_commands(message)





@bot.command()
async def CTA_season_leap(context):

    print(Fore.MAGENTA + Style.BRIGHT + f"\nCTA_season_leap has been called by {context.author.name}")
    if await Communication.authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted\n")

        dialogue_checker_loop.cancel()

        signed_up_user_ids = await API.get_signed_up_ids()
        dialogue_initiator = Dialogue.DialogueInitiator()
        dialogue_builders = []

        for role in Config.leap_roles:

            users = await Communication.get_role_members(context, role)

            if len(users) < 1:
                print(Fore.YELLOW + Style.NORMAL + "no members of the following role were messaged: {role}")

            else:
                print(f"{len(users)} members of the following role were messaged: {role}")


            for user in users:

                if f"{user.id}" not in signed_up_user_ids:

                    builder = await dialogue_initiator.initiate_SeasonLeap(user_id=user.id, role=role)
                    dialogue_builders.append(builder)

        current_builders = await Storage.read_dialogue_builders(list_name=Config.dialogue_file_name)
        current_builders.extend(dialogue_builders)
        await Storage.store_dialogue_builders(list_name=Config.dialogue_file_name, dialogue_builders=current_builders)

        dialogue_checker_loop.start()

    else:

        print(Fore.RED + Style.NORMAL + "request has been denied")
        await Communication.send_request_denial(context.author)



@bot.command()
async def get_leap_result(context):

    print(Fore.RESET + Style.BRIGHT + f"\nLeap results requested by {context.author.name}")

    if await Communication.authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        response = f"Leap results: " \
                   f"\n**contacted:** \n{await Storage.read_list_no_id(Config.contacted_leap_file_name)} " \
                   f"\n**declined:** \n{await Storage.read_list_no_id(Config.declined_leap_file_name)} " \
                   f"\n**confirmed:** \n{await Storage.read_list_no_id(Config.remaining_leap_file_name)}"

        await Communication.send_info_message(context.author, response)

    else:

        print(Fore.RED + Style.NORMAL + "request has been denied")
        await Communication.send_request_denial(context.author)






@bot.command()
async def CTA_season_sign_up(context):

    print(Fore.MAGENTA + Style.BRIGHT + f"\nCTA_season_sign_up has been called by {context.author.name}")
    if await Communication.authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        dialogue_checker_loop.cancel()

        excluded_users = []
        signed_up_user_ids = await API.get_signed_up_ids()

        dialogue_initiator = Dialogue.DialogueInitiator()
        dialogue_builders = []

        for signup in signed_up_user_ids:

            user = Config.bot.get_user(signup)
            excluded_users.append(user)


        # for role in Config.leap_roles:
        for role in ["Bronze"]:

            users = await Communication.get_role_members(context, role)
            excluded_users.extend(users)

        for role in Config.sign_up_roles:

            users = await Communication.get_role_members(context, role)
            included_users = [user for user in users if user not in excluded_users]

            for user in included_users:

                builder = await dialogue_initiator.initiate_SeasonInvite(user_id=user.id)
                dialogue_builders.append(builder)

        current_builders = await Storage.read_dialogue_builders(list_name=Config.dialogue_file_name)
        current_builders.extend(dialogue_builders)
        await Storage.store_dialogue_builders(list_name=Config.dialogue_file_name, dialogue_builders=current_builders)

        dialogue_checker_loop.start()



    else:

        print(Fore.RED + Style.NORMAL + "request has been denied")
        await Communication.send_request_denial(context.author)




@bot.command()
async def get_sign_up_result(context):

    print(Fore.RESET + Style.BRIGHT + f"\nInvite results requested by {context.author.name}")

    if await Communication.authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        response = f"Invite results: " \
                   f"\n**didn't respond**: \n{await Storage.read_list_no_id(Config.contacted_invite_file_name)}" \
                   f"\n**declined**: \n{await Storage.read_list_no_id(Config.declined_invite_file_name)}" \
                   f"\n**pending BP answer**: \n{await Storage.read_list_no_id(Config.pending_invite_file_name)}" \
                   f"\n**confirmed:** \n{await Storage.read_list_no_id(Config.confirmed_invite_file_name)} "

        await Communication.send_info_message(context.author, response)

    else:

        print(Fore.YELLOW + Style.NORMAL + "request has been denied")
        await Communication.send_request_denial(context.author)




@bot.command()
async def get_global_sign_ups(context):

    print(Fore.RESET + Style.BRIGHT + f"\nGlobal sign ups requested by {context.author.name}")

    if await Communication.authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        sign_up_ids = await API.get_signed_up_ids()
        signed_up_users = []

        for user_id in sign_up_ids:

            print(user_id)
            user = bot.get_user(int(user_id))
            print(user)

            if user is not None:
                signed_up_users.append([user.name])

        response = f"**{len(signed_up_users)} Global sign ups**: \n" \
                   f"{signed_up_users}"

        await Communication.send_info_message(context.author, response)

    else:

        print(Fore.YELLOW + Style.NORMAL + "request has been denied")
        await Communication.send_request_denial(context.author)







@bot.command()
async def send_json(context):
    message = "Here's the blueprint for the next season of PORC"
    data = await API.get_plan_blueprint()

    user = context.author

    # 2. Save the data to a JSON file
    filename = "MatchPlanBlueprint.json"
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    # 3. Send the file in the Discord channel
    with open(filename, "rb") as file:
        await context.send(message)
        await context.send("Here's your JSON file! :3", file=discord.File(file, filename))




@bot.command()
async def read_json(context):
    print(Fore.RESET + Style.BRIGHT + f"\nSeason start requested by {context.author.name}")

    if await Communication.authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        if context.message.attachments:

            for attachment in context.message.attachments:

                # Handle specific file types (e.g., JSON files)
                if attachment.filename.endswith(".json"):
                    try:
                        # Read the file contents
                        file_bytes = await attachment.read()
                        json_data = json.loads(file_bytes.decode("utf-8"))

                        print(Fore.GREEN + Style.NORMAL + "Provided JSON file successfully parsed:\n", json_data)

                        server_response = await API.post_plan_blueprint(json_data)

                        if server_response != "None":

                            await context.send(f"**Request failed, server gave the following error**: \n{server_response}")

                        else:

                            await context.send(f"**Request successful**")

                    except json.JSONDecodeError:

                        print(Fore.YELLOW + Style.NORMAL + "Provided JSON file could not be read")
                        await context.send(f"JSON file couldn't be read.")
                else:

                    print(Fore.YELLOW + Style.NORMAL + "Provided file was not of format JSON.")
                    await context.send(f"Provided file needs to be of format JSON.")
        else:

            print(Fore.YELLOW + Style.NORMAL + "No attachments found in message")
            await context.send("No attachments found in message :(")

    else:

        print(Fore.YELLOW + Style.NORMAL + "request has been denied")
        await Communication.send_request_denial(context.author)



@bot.command()
async def dialogue_tester(context):
    initiator = Dialogue.DialogueInitiator()
    builder = await initiator.initiate_SeasonLeap(user_id=context.author.id, role="meteorite")
    dialogue = await builder.build()
    print(builder)
    await dialogue.check()
    await Storage.store_dialogue_builders(list_name="Dialogues/Dialogues.json", dialogue_builders=[dialogue.getBuilder()])
    print(await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json"))











bot.run(token)