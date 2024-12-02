import discord
from discord.ext import tasks, commands
import SecurityModule
import json

# Setup security module for encryption and decryption
securityModule = SecurityModule

# Bot prefix UwU (you can change it if you like)!
intents = discord.Intents.default()
intents.members = True  # Enable Server Members Intent
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

prompt = "This is a test, please react with ❌ or ✅ depending on how you feel about nuclear war"
accept_emoji = "✅"
decline_emoji = "❌"

contacted_file_name = "Contacted_Users.json"

# invloved_roles = ["Meteorite", "Malachite","Adamantium", "Mithril", "Platinum", "Diamond", "Gold", "Silver", "Bronze", "Steel", "Copper", "Iron", "Stone"]
invloved_roles = ["Mod"]


@tasks.loop(minutes=3)
async def reaction_checker():
    print(f"{bot.user} is now online! OwO")

    print(f"checking on contacted users")
    user_list = []

    with open(contacted_file_name, "r") as file:
        try:
            user_list.extend(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    with open("Remaining_Users.json", "r") as file:
        try:
            user_list.extend(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            user_list.extend([])

    with open("Declining_Users.json", "r") as file:
        try:
            user_list.extend(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            user_list.extend([])



    for user_data in user_list:

        user = bot.get_user(user_data[1])
        reactions = await check_reaction(user)

        denial = False
        approval = False

        for reaction in reactions:

            if reaction == accept_emoji:
                approval = True

            if reaction == decline_emoji:
                denial = True

        if approval & (not denial):
            await store_user("Remaining_Users.json", user)
            await remove_user(contacted_file_name, user)
            await remove_user("Declining_Users.json", user)
            print(f"\nuser {user.name} approved")

        elif denial & (not approval):
            await store_user("Declining_Users.json", user)
            await remove_user(contacted_file_name, user)
            await remove_user("Remaining_Users.json", user)
            print(f"\nuser {user.name} opted out")

    print(f"\ncaught up with responses ^^")



# Event: when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is now online! OwO")
    reaction_checker.start()


@bot.event
async def on_reaction_add(reaction, reacter):

    if not reacter.id == bot.user.id:

        print(f"\nsomeone reacted to my message ^^")

        user = bot.get_user(reacter.id)
        reactions = await check_reaction(user)

        denial = False
        approval = False

        for reaction in reactions:

            if reaction == accept_emoji:
                approval = True

            elif reaction == decline_emoji:
                denial = True

        if approval & (not denial):
            await store_user("Remaining_Users.json", user)
            await remove_user(contacted_file_name, user)
            await remove_user("Declining_Users.json", user)
            print(f"\nuser {user.name} approved")

        elif denial & (not approval):
            await store_user("Declining_Users.json", user)
            await remove_user(contacted_file_name, user)
            await remove_user("Remaining_Users.json", user)
            print(f"\nuser {user.name} opted out")




@bot.command()
async def CTA_season_invite(context):

    for role in invloved_roles:

        users = await get_role_members(context, role)

        for user in users:

            await send_prompt_message(user)
            await store_user(contacted_file_name, user)





@bot.command()
async def send_prompt_message(user_target):
    print(f"\nsending a message to user: {user_target}")

    try:
        message = await user_target.send(f"{prompt}")

        await message.add_reaction(accept_emoji)
        await message.add_reaction(decline_emoji)

    except:
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
async def store_user(list_name, User):
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    double_check = True
    user_data = [User.name, User.id]
    for entry in user_list:
        if user_data == entry:
            double_check = False

    if double_check:
        user_list.append([User.name, User.id])

    with open(list_name, "w") as file:
        json.dump(user_list, file)



# @bot.command()
async def remove_user(list_name, User):
    # list_name = "Contacted_Users.json"
    # User = context.author

    with open(list_name, "r") as file:
        try:
            user_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_list = []

    user_data = [User.name, User.id]
    try:
        user_list.remove(user_data)
    except:
        print(f"\nNo element to remove in user list")


    with open(list_name, "w") as file:
        json.dump(user_list, file)











async def get_user_reaction(message, reacting_user):
    reactions = message.reactions
    user_reactions = []

    for reaction in reactions:
        reacting_users = await reaction.users().flatten()
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
    chat_history = await dm_channel.history().flatten()

    # potential error, but shouldnt happen given the conditions to get on the list
    for message in chat_history:
        if message.content == prompt:
            prompt_message = message
            break

    user_reactions = await get_user_reaction(prompt_message, user)

    print(f"User {user.name} reacted with emojis: {user_reactions}")
    return user_reactions







bot.run()