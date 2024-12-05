import discord
from discord.ext import tasks, commands
import SecurityModule
import StorageModule as Storage
from colorama import Fore, Style
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

stay_prompt = f'''
Hello, I'm PORC bot, the newest member of the PORC organization team.
As of now you are an active member of the second season of the PORC league which will end December 6th.
If you want to **continue being a part of part of PORC for the third season please react with** ✅ to this message.
If you react with ❌ or do not react to this message you will **not be entered** into the third season of PORC.
Thanks for participating and we hope you enjoy your time with PORC.

**Do you want to participate in the third season of PORC?**
'''.strip()


invite_prompt = f'''Hello, I'm PORC bot, the newest member of the PORC organization team.
You are receiving this message because you currently have the competitor role but are not competing in the PORC league.
If you want to **sign up for the third season of PORC**, which will start **December 7th**, please react with ✅ to this message.
If you react with ❌ or do not react, you will **not be entered** into the third season of PORC.
In case you already signed up for PORC season 3 via the form, feel free to accept or ignore this message.

**Do you want to participate in the third season of PORC?**'''.strip()

invite_confirm_prompt = f'''What is your current BP?'''.strip()

invite_confirmation_message = f'''Congrats, you have been successfully signed up for PORC season 3!'''.strip()


accept_emoji = "✅"
decline_emoji = "❌"

contacted_leap_file_name = "season_leaps/Contacted_Users.json"
remaining_leap_file_name = "season_leaps/Remaining_Users.json"
declined_leap_file_name = "season_leaps/Declining_Users.json"

contacted_invite_file_name = r"season_invites\Invited_Users.json"
pending_invite_file_name = r"season_invites\Pending_Confirms.json"
confirmed_invite_file_name = r"season_invites\Confirmed_Users.json"

leap_roles = ["Meteorite", "Malachite", "Adamantium", "Mithril", "Platinum", "Diamond", "Gold", "Silver", "Bronze", "Steel", "Copper", "Iron", "Stone"]
# leap_roles = ["DEV"]

# sign_up_roles = ["Competitor"]
sign_up_roles = ["Mod"]

authority_roles = ["DEV"]
request_denial = "You do not have the necessary permissions to execute this command"

@tasks.loop(minutes=2)
async def leap_checker():

    # print(f"\nReading out all list: "
    #      f"\ncontacted{await Storage.read_list(contacted_leap_file_name)} "
    #      f"\ndeclined{await Storage.read_list(declined_leap_file_name)} "
    #      f"\napproval{await Storage.read_list(remaining_leap_file_name)}")
    print(Fore.RESET + Style.NORMAL + f"checking on contacted users")

    user_list = await Storage.read_list(contacted_leap_file_name)
    user_list.extend(await Storage.read_list(remaining_leap_file_name))
    user_list.extend(await Storage.read_list(declined_leap_file_name))


    for user_data in user_list:

        # print(f"\nChecking user: {user_data}")
        user = bot.get_user(user_data[2])
        role = user_data[1]
        reactions = await check_reaction(user, stay_prompt)

        denial = False
        approval = False

        for reaction in reactions:

            if reaction == accept_emoji:
                approval = True

            if reaction == decline_emoji:
                denial = True

        if approval & (not denial):
            await Storage.store_user(remaining_leap_file_name, user, role)
            await Storage.remove_user(contacted_leap_file_name, user, role)
            await Storage.remove_user(declined_leap_file_name, user, role)
            # print(f"\nuser {user.name} approved")

        elif denial & (not approval):
            await Storage.store_user(declined_leap_file_name, user, role)
            await Storage.remove_user(contacted_leap_file_name, user, role)
            await Storage.remove_user(remaining_leap_file_name, user, role)
            # print(f"\nuser {user.name} opted out")

    print(Fore.GREEN + Style.NORMAL + f"caught up with responses ^^")






@tasks.loop(minutes=3)
async def invite_reaction_checker():

    print(Fore.RESET + Style.NORMAL + f"\nchecking on invited users")
    # print(f"Invited users: "
    #      f"\n{await Storage.read_list(contacted_invite_file_name)}")

    user_list = await Storage.read_list(contacted_invite_file_name)


    for user_data in user_list:

        # print(Fore.RESET + Style.RESET_ALL + f"\nChecking user: {user_data}")
        user = bot.get_user(user_data[2])
        reactions = await check_reaction(user, invite_prompt)

        denial = False
        approval = False

        for reaction in reactions:

            if reaction == accept_emoji:
                approval = True

            if reaction == decline_emoji:
                denial = True

        if approval & (not denial):
            await Storage.store_user(pending_invite_file_name, user, "")
            await send_info_message(user, invite_confirm_prompt)
            await Storage.remove_user(contacted_invite_file_name, user, "")
            # print(f"\nuser {user.name} approved the invite")

        elif denial & (not approval):
            await Storage.remove_user(contacted_invite_file_name, user, "")
            # print(f"\nuser {user.name} declined the invite")

    print(Fore.GREEN + Style.NORMAL + f"checked all invite reactions ^^")





@tasks.loop(minutes=3)
async def invite_response_checker():

    print(Fore.RESET + Style.NORMAL + f"\nchecking on approved invited users")
    # print(f"Approved invited users: "
    #      f"\n{await Storage.read_list(pending_invite_file_name)}")

    user_list = await Storage.read_list(pending_invite_file_name)


    for user_data in user_list:

        print(f"\nChecking user: {user_data}")
        user = bot.get_user(user_data[2])
        responses = await check_response(user, invite_confirm_prompt)

        if len(responses) > 0:

            await Storage.store_user(confirmed_invite_file_name, user, responses)
            await send_info_message(user, invite_confirmation_message)
            await Storage.remove_user(pending_invite_file_name, user, "")

    print(Fore.GREEN + Style.NORMAL + f"checked all invite responses ^^")



# Event: when the bot is ready
@bot.event
async def on_ready():
    print(Fore.RESET + Style.BRIGHT + f"{bot.user} is now online! OwO")
    leap_checker.start()
    invite_reaction_checker.start()
    invite_response_checker.start()


@bot.event
async def on_reaction_add(reaction, user):
    if user.id != bot.user.id:
        leap_checker.restart()
        invite_reaction_checker.restart()



@bot.event
async def on_message(message):
    if message.author.id != bot.user.id:

        # checks if message is dm
        if isinstance(message.channel, discord.DMChannel):
            invite_response_checker.restart()

        await bot.process_commands(message)



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
async def CTA_season_leap(context):

    print(Fore.RESET + Style.BRIGHT + f"\nCTA_season_leap has been called by {context.author}")
    if await authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted\n")

        for role in leap_roles:

            users = await get_role_members(context, role)

            if len(users) < 1:
                print(Fore.YELLOW + Style.NORMAL + "no members of the following role were messaged: {role}")

            else:
                print(f"{len(users)} members of the following role were messaged: {role}")


            for user in users:

                await send_prompt_message(user, stay_prompt)
                await Storage.store_user(contacted_leap_file_name, user, role)

    else:

        print(Fore.RED + Style.NORMAL + "request has been denied")
        await send_request_denial(context.author)



@bot.command()
async def get_leap_result(context):

    print(Fore.RESET + Style.BRIGHT + f"\nLeap results requested by {context.author.name}")

    if await authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        response = f"Leap results: " \
                   f"\n**contacted:** \n{await Storage.read_list_no_id(contacted_leap_file_name)} " \
                   f"\n**declined:** \n{await Storage.read_list_no_id(declined_leap_file_name)} " \
                   f"\n**confirmed:** \n{await Storage.read_list_no_id(remaining_leap_file_name)}"

        await send_info_message(context.author, response)

    else:

        print(Fore.RED + Style.NORMAL + "request has been denied")
        await send_request_denial(context.author)






@bot.command()
async def CTA_season_sign_up(context):

    print(Fore.RESET + Style.BRIGHT + "\nCTA_season_sign_up has been called by {context.author}")
    if await authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        excluded_users = []
        leap_roles = ["Bronze", "Meteorite"]


        for role in leap_roles:

            users = await get_role_members(context, role)
            excluded_users.extend(users)

        for role in sign_up_roles:

            users = await get_role_members(context, role)
            included_users = [user for user in users if user not in excluded_users]

            for user in included_users:

                await send_prompt_message(user, invite_prompt)
                # print(f"would have sent prompt message to {user.name}")
                await Storage.store_user(contacted_invite_file_name, user, "")

    else:

        print(Fore.RED + Style.NORMAL + "request has been denied")
        await send_request_denial(context.author)




@bot.command()
async def get_sign_up_result(context):

    print(Fore.RESET + Style.BRIGHT + f"\nInvite results requested by {context.author.name}")

    if await authenticate_user(context, context.author):
        print(Fore.GREEN + Style.NORMAL + "request has been accepted")

        response = f"Invite results: " \
                   f"\n**confirmed:** {await Storage.read_list_no_id(confirmed_invite_file_name)} "

        await send_info_message(context.author, response)

    else:

        print(Fore.YELLOW + Style.NORMAL + "request has been denied")
        await send_request_denial(context.author)






async def send_prompt_message(user_target, prompt):
    print(Fore.RESET + Style.NORMAL + f"\nsending a prompt message to user: {user_target}")

    try:
        message = await user_target.send(f"{prompt}")

        await message.add_reaction(accept_emoji)
        await message.add_reaction(decline_emoji)

    except discord.Forbidden:
        print(Fore.RED + Style.NORMAL + "An issue occurred while sending dm")




# TODO: Make this send message in channel rather then dm
async def send_request_denial(user_target):
    print(Fore.YELLOW + Style.NORMAL + "\nsending a request denial message to user: {user_target}")

    try:
        await user_target.send(f"{request_denial}")

    except discord.Forbidden:
        print(Fore.RED + Style.NORMAL + f"An issue occurred while sending dm")




async def send_info_message(user_target, content):
    print(Fore.RESET + Style.NORMAL + f"\nsending an info message to user: {user_target}")

    try:
        message = await user_target.send(f"{content}")

    except discord.Forbidden:
        print(Fore.RED + Style.NORMAL + "An issue occurred while sending dm")


# @bot.command()
async def get_role_members(context, role_name):
    # role_name = "Mod"
    # print(f"\ngetting members of role: {role_name}")

    server = context.guild
    if not server:
        print(Fore.RED + Style.NORMAL + f"\nA problem occurred while fetching discord server")

    role = discord.utils.get(server.roles, name=role_name)
    if not role:
        print(Fore.RED + Style.NORMAL + f"\nA problem occurred while fetching discord role")

    # Dont know Python syntax well enough to fully understand whats going on here, but it should filter server members for members with role
    members_with_role = [member for member in server.members if role in member.roles]

    # print(f"\nFound the following members with role {role_name}: \n{members_with_role}")
    return members_with_role













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
async def check_reaction(user, prompt):
    # prompt = "prompt placeholder owo"
    # user_data = context.author

    # user = await bot.fetch_user(user_data.id)
    try:
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

        # if len(user_reactions) > 0:
            # print(f"User {user.name} reacted with emojis: {user_reactions}")

    except:
        user_reactions = []

    return user_reactions






# returns either empty list or list with one element
async def check_response(user, prompt):

    try:
        dm_channel = await user.create_dm()

        # apparently the output of .history is an async iterator, therefore flatten
        # chat_history = await dm_channel.history().filter(lambda m: m.author.id == bot.user.id).flatten()
        chat_history = []
        async for message in dm_channel.history():
            chat_history.append(message)

        # potential error, but shouldnt happen given the conditions to get on the list
        response_messages = []
        response_index = -1
        for index, message in enumerate(chat_history):
            if (message.content == prompt) & (response_index == -1):

                response_index = index - 1
                while response_index >= 0:
                    if chat_history[response_index].author.id == bot.user.id:
                        response_index += -1
                    else:
                        break

        if response_index >= 0:
            response_messages.append(chat_history[response_index].content)

        # if len(response_messages) > 0:
            # print(f"User {user.name} responded with: {response_messages[0]}")

    except:
        response_messages = []

    return response_messages







bot.run(token)