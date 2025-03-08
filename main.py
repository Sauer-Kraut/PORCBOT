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
from flask import Flask, request, jsonify
import threading
import asyncio

from DialogueRoutes.SeasonLeap import LeapData

# Setup security module for encryption and decryption
securityModule = SecurityModule.SecurityModule()

bot = Config.bot

app = Flask(__name__)

token = os.getenv("PORC_TOKEN")




def run_flask():
    app.run(debug=False, host='127.0.0.1', port=8085)



@app.route('/porcbot/event', methods=['PUT'])
def plan_event():
    print("received plan event put request")
    try:
        # Get data from POST request
        data = request.get_json()
        Storage.write_request_to_file(data)

        print("Event planing started successfully!")
        return jsonify({"message": f"Event planing started successfully!"}), 200
    except Exception as e:
        print(Fore.RED + f"error occurred: {e}")
        return jsonify({"error": str(e)}), 500


async def initiate_match_request(data):
    start_timestamp = data['start_timestamp']
    challenger_id = data['challenger_id']
    opponent_id = data['opponent_id']
    league = data['league']

    initiator = Dialogue.DialogueInitiator()
    builder = await initiator.initiate_MatchRequest(user_id=306467062530965514, challenger_id=int(challenger_id), opponent_id=int(opponent_id), league="league", start_timestamp=int(start_timestamp))
    builders = await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json")
    builders.append(builder)
    await Storage.store_dialogue_builders(list_name="Dialogues/Dialogues.json", dialogue_builders=builders)


async def process_request(data):
    await initiate_match_request(data)
    print(f"Processed request: {data}")

async def request_handler():
    """Continuously check for new requests in the file."""
    while True:
        await asyncio.sleep(5)  # Adjust polling interval as needed

        if not os.path.exists(Config.REQUESTS_FILE):
            continue

        try:
            with open(Config.REQUESTS_FILE, "r", encoding="utf-8") as f:
                recvRequests = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            recvRequests = []

        if recvRequests:
            first_request = recvRequests.pop(0)  # Get the first request

            await process_request(first_request)

            # Save the updated list back to the file
            with open(Config.REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump(recvRequests, f, indent=4)



checking_dialogues = False

@tasks.loop(minutes=6)
async def dialogue_checker_loop():
    global checking_dialogues
    checking_dialogues = True

    print(Fore.RESET + Style.NORMAL + "Checking up on running conversations OwO")

    dialogue_builders = await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json")
    await Storage.drop_dialogue_lock()

    for index in range(len(dialogue_builders)):

        try:

            builders = await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json")

            updated_builders = []
            current_index = 0
            for builder in builders:

                if current_index == index:

                    dialogue = await builders[index].build()
                    username = Config.bot.get_user(dialogue.dialogue_data.user_id).name
                    print(Fore.RESET + Style.NORMAL + f"\nchecking dialogue of type: " + Fore.RESET + Style.BRIGHT + f"{dialogue.dialogue_data.kind}" + Fore.RESET + Style.NORMAL + " with user: " + Fore.RESET + Style.BRIGHT + f"{username}")
                    await dialogue.check()

                    # will cause the following builder to get skipped for his check in case of finish but not to tragic since it repeats all 6 minutes
                    if dialogue.index != 600:
                        updated_builders.append(dialogue.getBuilder())

                    else:
                        print(Fore.RESET + Style.NORMAL + f"Finished a dialogue")

                else:
                    updated_builders.append(builder)

                current_index += 1

            await Storage.store_dialogue_builders(list_name="Dialogues/Dialogues.json", dialogue_builders=updated_builders)

        except Exception as e:
            print(Fore.RED + f"error occurred while checking dialogue: {e}")
            await Storage.drop_dialogue_lock()

    checking_dialogues = False


# Event: when the bot is ready
@bot.event
async def on_ready():
    print(Fore.RED + Style.BRIGHT + "WARNING: ignore the other guys warning, I know what Im doing")
    print(Fore.RESET + Style.BRIGHT + f"{bot.user} is now online! OwO")
    dialogue_checker_loop.start()
    bot.loop.create_task(request_handler())


@bot.event
async def on_reaction_add(reaction, user):
    global checking_dialogues
    if user.id != bot.user.id:
        try:
            print("received reaction")
            if checking_dialogues is not True:
                dialogue_checker_loop.restart()

        except:
            print(Fore.RED + Style.NORMAL + "\ncouldn't restart a loop\n")


@bot.event
async def on_message(message):
    global checking_dialogues
    if message.author.id != bot.user.id:

        # checks if message is dm
        if isinstance(message.channel, discord.DMChannel):
            print("received message")
            try:
                if checking_dialogues is not True:
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
                print(Fore.YELLOW + Style.NORMAL + f"no members of the following role were messaged: {role}")

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
        signed_up_user_ids = {int(user_id) for user_id in await API.get_signed_up_ids()}

        dialogue_initiator = Dialogue.DialogueInitiator()
        dialogue_builders = []

        excluded_users.extend(signed_up_user_ids)

        # for role in ["Bronze"]:
        for role in Config.leap_roles:

            users = await Communication.get_role_members(context, role)

            for user in users:

                excluded_users.append(user.id)

        for role in Config.sign_up_roles:

            users = {user.id for user in await Communication.get_role_members(context, role)}
            included_users = [user for user in users if user not in excluded_users]

            for user in included_users:

                builder = await dialogue_initiator.initiate_SeasonInvite(user_id=user)
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
    await Storage.get_dialogue_lock()
    await Storage.store_dialogue_builders(list_name="Dialogues/Dialogues.json", dialogue_builders=[dialogue.getBuilder()])
    print(await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json"))
    await Storage.drop_dialogue_lock()



@bot.command()
async def event_tester(context):
    await Communication.create_event(start_timestamp=1741028400, channel_id=Config.stage_channel_ids[0], name="test event", description="something exiting is cooking")


@bot.command()
async def match_request_tester(context):
    initiator = Dialogue.DialogueInitiator()
    builder = await initiator.initiate_MatchRequest(user_id=context.author.id, challenger_id=178905571682942976, opponent_id=306467062530965514, league="Meteorite", start_timestamp=1741460400)
    builders = await Storage.read_dialogue_builders(list_name="Dialogues/Dialogues.json")
    builders.append(builder)
    await Storage.store_dialogue_builders(list_name="Dialogues/Dialogues.json", dialogue_builders=builders)



@bot.command()
async def match_status_tester(context):
    match_id = "1002V306467062530965514@1741348800"
    res = await API.get_match_status(match_id)









flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

bot.run(token)