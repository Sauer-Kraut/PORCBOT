import discord
from colorama import Fore, Style
from datetime import datetime, timezone, timedelta
import random


accept_emoji = "✅"
decline_emoji = "❌"

authority_roles = ["DEV"]
request_denial = "You do not have the necessary permissions to execute this command"

async def authenticate_user(context, user):

    authenticated = False

    for role in authority_roles:

        authenticated_members = await get_role_members(context, role)

        for member in authenticated_members:

            if user.id == member.id:

                authenticated = True
                break

    return authenticated



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
async def check_reaction(user, prompt: str):
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

        if len(user_reactions) > 0:
            print(Fore.RESET + Style.NORMAL + f"User {user.name} reacted with emojis: {user_reactions}")

        else:
            print(Fore.RESET + Style.NORMAL + "no reaction found")

    except Exception as err:
        print(Fore.RED + Style.NORMAL + f"a problem occurred while checking for reactions: {err}")
        user_reactions = []

    return user_reactions






# returns either empty list or list with one element
async def check_response(user, prompt: str):

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
                    if chat_history[response_index].author.id == config.bot.user.id:
                        response_index += -1
                    else:
                        break

        if response_index >= 0:
            response_messages.append([chat_history[response_index].content, chat_history[response_index].attachments])

        if len(response_messages) > 0:
            print(Fore.RESET + Style.NORMAL + f"User {user.name} responded with: {response_messages[0]}")

    except Exception as err:
        print(Fore.RED + Style.NORMAL + f"a problem occurred while checking for responses: {err}")
        response_messages = []

    return response_messages





async def create_event(start_timestamp: int, channel_id: int, name: str, description: str):

    guild = config.bot.get_guild(config.porc_guild_id)
    channel = guild.get_channel(channel_id)

    # Check if the provided channel is valid
    if channel is None:
        print(Fore.RED + Style.NORMAL + f"Channel could not be found")
        return None
    if not isinstance(channel, discord.StageChannel):
        print(Fore.RED + Style.NORMAL + f"Channel is not a stage channel")
        return None

    start_time = datetime.fromtimestamp(start_timestamp, tz=timezone.utc)  # 5 min from now
    end_time = start_time + timedelta(hours=1)  # Lasts 1 hour

    try:
        # Create the event in the selected voice channel
        event = await guild.create_scheduled_event(
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            entity_type=discord.EntityType.stage_instance,  # Voice event
            channel=channel,  # Set the event to the selected channel
            privacy_level=discord.PrivacyLevel.guild_only
        )
        print(Fore.RESET + Style.NORMAL + "Event created successfully")
        return event
    except discord.Forbidden:
        print(Fore.RED + Style.NORMAL + f"Missing permissions to create events")
        return None
    except discord.HTTPException as e:
        print(Fore.RED + Style.NORMAL + f"failed to create event: {e}")
        return None



async def create_match_event(start_timestamp: int, challenger_username: str, opponent_username: str, league: str):

    event_name = f"[{league}] {challenger_username} vs. {opponent_username}"
    channel_id = config.stage_channel_ids[random.randint(0, 2)]
    description = ""

    return await create_event(start_timestamp=start_timestamp, channel_id=channel_id, description=description, name=event_name)
