import discord
from discord.ext import tasks, commands
import SecurityModule
import json
import os

# Setup security module for encryption and decryption
securityModule = SecurityModule.SecurityModule()

# Bot prefix UwU (you can change it if you like)!
intents = discord.Intents.default()
intents.members = True  # Enable Server Members Intent
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

token = os.getenv("PORC_TOKEN")

prompt = "This is a test, please react with ❌ or ✅ depending on how you feel about nuclear war"
accept_emoji = "✅"
decline_emoji = "❌"

contacted_file_name = "Contacted_Users.json"

# involved_roles = ["Meteorite", "Malachite","Adamantium", "Mithril", "Platinum", "Diamond", "Gold", "Silver", "Bronze", "Steel", "Copper", "Iron", "Stone"]
involved_roles = ["DEV"]

authority_roles = ["DEV"]
request_denial = "You do not have the necessary permissions to execute this command"

@tasks.loop(minutes=2)
async def reaction_checker():
    print(f"{bot.user} is now online! OwO")

    print(f"\nReading out all list: \ncontacted{await read_list(contacted_file_name)} \ndeclined{await read_list('Declining_Users.json')} \napproval{await read_list('Remaining_Users.json')}")
    print(f"checking on contacted users")

    user_list = await read_list(contacted_file_name)
    user_list.extend(await read_list("Remaining_Users.json"))
    user_list.extend(await read_list("Declining_Users.json"))


    for user_data in user_list:

        print(f"\nChecking user: {user_data}")
        user = bot.get_user(user_data[2])
        role = user_data[1]
        reactions = await check_reaction(user)

        denial = False
        approval = False

        for reaction in reactions:

            if reaction == accept_emoji:
                approval = True

            if reaction == decline_emoji:
                denial = True

        if approval & (not denial):
            await store_user("Remaining_Users.json", user, role)
            await remove_user(contacted_file_name, user, role)
            await remove_user("Declining_Users.json", user, role)
            print(f"\nuser {user.name} approved")

        elif denial & (not approval):
            await store_user("Declining_Users.json", user, role)
            await remove_user(contacted_file_name, user, role)
            await remove_user("Remaining_Users.json", user, role)
            print(f"\nuser {user.name} opted out")

    print(f"\ncaught up with responses ^^")



# Event: when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is now online! OwO")
    reaction_checker.start()


async def authenticate_user(context, user):

    authenticated = False

    for role in authority_roles:

        authenticated_members = await get_role_members(context, role)

        for member in authenticated_members:

            if user.id == member.id:

                authenticated = True
                break

    return authenticated





@bot.command()
async def CTA_season_invite(context):

    print(f"\nCTA_season_invite has been called")
    if await authenticate_user(context, context.author):

        for role in involved_roles:

            users = await get_role_members(context, role)

            for user in users:

                await send_prompt_message(user)
                await store_user(contacted_file_name, user, role)

    else:

        await send_request_denial(context.author)



@bot.command()
async def get_invite_result(context):

    print(f"\nInvite results requested by {context.author.name}")

    if await authenticate_user(context, context.author):
        print("accepted request")

        response = f"Invite results: " \
                   f"\ncontacted: {await read_list(contacted_file_name)} " \
                   f"\ndeclined: {await read_list('Declining_Users.json')} " \
                   f"\nconfirmed: {await read_list('Remaining_Users.json')}"

        await sent_info_message(context.author, response)

    else:
        print("denied request")
        await send_request_denial(context.author)






async def send_prompt_message(user_target):
    print(f"\nsending a prompt message to user: {user_target}")

    try:
        message = await user_target.send(f"{prompt}")

        await message.add_reaction(accept_emoji)
        await message.add_reaction(decline_emoji)

    except discord.Forbidden:
        print(f"An issue occurred while sending dm")




# TODO: Make this send message in channel rather then dm
async def send_request_denial(user_target):
    print(f"\nsending a request denial message to user: {user_target}")

    try:
        await user_target.send(f"{request_denial}")

    except discord.Forbidden:
        print(f"An issue occurred while sending dm")




async def sent_info_message(user_target, content):
    print(f"\nsending an info message to user: {user_target}")

    try:
        message = await user_target.send(f"{content}")

    except discord.Forbidden:
        print(f"An issue occurred while sending dm")


# @bot.command()
async def get_role_members(context, role_name):
    # role_name = "Mod"
    print(f"\ngetting members of role: {role_name}")

    server = context.guild
    if not server:
        print(f"\nA problem occurred while fetching discord server")

    role = discord.utils.get(server.roles, name=role_name)
    if not role:
        print(f"\nA problem occurred while fetching discord role")

    # Dont know Python syntax well enough to fully understand whats going on here, but it should filter server members for members with role
    members_with_role = [member for member in server.members if role in member.roles]

    print(f"\nFound the following members with role {role_name}: \n{members_with_role}")
    return members_with_role




# @bot.command()
async def store_user(list_name, User, role):
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
    user_data = [User.name, role, User.id]
    encrypted_user_data = securityModule.encrypt(user_data)
    for entry in user_list:
        decrypted_entry = securityModule.decrypt(entry)

        if user_data == decrypted_entry:
            double_check = False

    if double_check:
        user_list.append(encrypted_user_data)

    with open(list_name, "w") as file:
        json.dump(user_list, file)



async def read_list(list_name):
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
async def remove_user(list_name, User, role):
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    user_data = [User.name, role, User.id]
    for index, entry in enumerate(user_list):
        decrypted_entry = securityModule.decrypt(entry)

        if user_data == decrypted_entry:
            del user_list[index]

    with open(list_name, "w") as file:
        json.dump(user_list, file)











async def get_user_reaction(message, reacting_user):
    reactions = message.reactions
    user_reactions = []

    for reaction in reactions:

        reacting_users = []
        async for user in reaction.users():
            reacting_users.append(user)

        for user in reacting_users:

            if user == reacting_user:
                user_reactions.append(reaction.emoji)

    return user_reactions



# @bot.command()
async def check_reaction(user):
    # prompt = "prompt placeholder owo"
    # user_data = context.author

    # user = await bot.fetch_user(user_data.id)

    dm_channel = await user.create_dm()

    # apparently the output of .history is an async iterator, therefore flatten
    # chat_history = await dm_channel.history().filter(lambda m: m.author.id == bot.user.id).flatten()
    chat_history = []
    async for message in dm_channel.history():
        chat_history.append(message)

    # potential error, but shouldnt happen given the conditions to get on the list
    for message in chat_history:
        if message.content == prompt:
            prompt_message = message
            break

    user_reactions = await get_user_reaction(prompt_message, user)

    print(f"User {user.name} reacted with emojis: {user_reactions}")
    return user_reactions







bot.run(token)