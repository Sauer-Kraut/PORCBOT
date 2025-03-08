import discord
from discord.ext import tasks, commands


blueprint_prompt = f'''
Here's the blueprint for the next division of PORC. 
Please **correctly place all members** and enter **timestamps for both the end of the season and the end of the brake following it**,
as well as **the discriminator** of the season.

When you are done you can commit your plan via !start_new_season with the file attached'''


accept_emoji = "✅"
decline_emoji = "❌"

contacted_leap_file_name = "./AppData/season_leaps/Contacted_Users.json"
remaining_leap_file_name = "./AppData/season_leaps/Remaining_Users.json"
declined_leap_file_name = "./AppData/season_leaps/Declining_Users.json"

contacted_invite_file_name = r"./AppData/season_invites/Invited_Users.json"
pending_invite_file_name = r"./AppData/season_invites/Pending_Confirms.json"
confirmed_invite_file_name = r"./AppData/season_invites/Confirmed_Users.json"
declined_invite_file_name = r"./AppData/season_invites/Declined_Invites.json"

dialogue_file_name = r"./AppData/Dialogues/Dialogues.json"

leap_roles = ["Meteorite", "Malachite", "Adamantium", "Mithril", "Platinum", "Diamond", "Gold", "Silver", "Bronze", "Steel", "Copper", "Iron", "Stone"]
# leap_roles = ["DEV"]

sign_up_roles = ["Competitor"]
# sign_up_roles = ["DEV"]

# Bot prefix UwU (you can change it if you like)!
intents = discord.Intents.default()
intents.members = True  # Enable Server Members Intent
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

porc_guild_id = 1264474928095297536
stage_channel_ids = [1280230793041674291, 1280231416918970389, 1280231175549489263]

REQUESTS_FILE = "./AppData/requests.json"
