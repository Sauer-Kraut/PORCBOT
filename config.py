import discord
from discord.ext import tasks, commands

# better version but to late to change now, for next season
# stay_prompt = f'''
# Hello, I'm PORC bot, the newest member of the PORC organization team.
# As of now, you are an active member of the second season of the PORC league, which will end on December 6th.
# If you want to **continue being a part of PORC for the third season, please react with** ✅ to this message.
# If you react with ❌ or do not react to this message, you will **not be entered** into the third season of PORC.
# Thanks for participating, and we hope you enjoy your time with PORC.

# **Do you want to participate in the third season of PORC?**
# '''.strip()



stay_prompt = f'''
Hello, I'm PORC bot, the new hire of the PORC organization team.
As of now you are an active member of the second season of the PORC league which will end December 6th.
If you want to **continue being a part of part of PORC for the third season please react to with** ✅ to this message.
If you react with ❌ or do not react to this message you will **not be entered** into the third season of PORC.
**Declining this message will take priority** over singups via other route like our website.
Thanks for participating and we hope you enjoy your time with PORC.

**Do you want to participate in the third season of PORC?**
'''.strip()


invite_prompt = f'''
Hello, I'm PORC bot, the newest member of the PORC organization team.
You are receiving this message because you currently have the competitor role but are not competing in the PORC league.
If you want to **sign up for the forth season of PORC**, which will start **December 18th**, please react with ✅ to this message.
If you react with ❌ or do not react, you will **not be entered** into the forth season of PORC.
**Declining this message will take priority** over singups via other route like our website.

**Do you want to participate in the third season of PORC?**
'''.strip()

invite_confirm_prompt = f'''What is your current BP?'''.strip()

invite_confirmation_message = f'''Congrats! **You are now signed up for PORC season 3**!
If you change your mind later, simply update your reaction to the invite message.'''.strip()

invite_decline_confirmation = f'''**Your decline has been registered successfully**!
If you change your mind later, simply update your reaction to the invite message.'''.strip()

application_withdrawal_confirmation = f'''**Your application has been withdrawn**.'''.strip()

application_reenter_confirmation = f'''**Your application has been reentered successfully**.'''.strip()


blueprint_prompt = f'''
Here's the blueprint for the next division of PORC. 
Please **correctly place all members** and enter **timestamps for both the end of the season and the end of the brake following it**,
as well as **the discriminator** of the season.

When you are done you can commit your plan via !start_new_season with the file attached'''


accept_emoji = "✅"
decline_emoji = "❌"

contacted_leap_file_name = "season_leaps/Contacted_Users.json"
remaining_leap_file_name = "season_leaps/Remaining_Users.json"
declined_leap_file_name = "season_leaps/Declining_Users.json"

contacted_invite_file_name = r"season_invites\Invited_Users.json"
pending_invite_file_name = r"season_invites\Pending_Confirms.json"
confirmed_invite_file_name = r"season_invites\Confirmed_Users.json"
declined_invite_file_name = r"season_invites\Declined_Invites.json"

dialogue_file_name = r"Dialogues/Dialogues.json"

# leap_roles = ["Meteorite", "Malachite", "Adamantium", "Mithril", "Platinum", "Diamond", "Gold", "Silver", "Bronze", "Steel", "Copper", "Iron", "Stone"]
leap_roles = ["DEV"]

# sign_up_roles = ["Competitor"]
sign_up_roles = ["DEV"]

# Bot prefix UwU (you can change it if you like)!
intents = discord.Intents.default()
intents.members = True  # Enable Server Members Intent
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)