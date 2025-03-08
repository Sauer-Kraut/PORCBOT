from src import StorageModule as Storage, ServerCommunicationModule as API
from src import config
from src.DailogeModule import DialoguePlan, DialogueStep

bot = config.bot


async def completion_script_0():
    async def evaluator(dialogue_data, approval: bool, no_resp: bool):
        # print("completion script 0 executing")
        if no_resp:
            return [-1, dialogue_data]

        elif approval:
            await Storage.store_user(config.remaining_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(config.contacted_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(config.declined_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)

            result = await API.sign_up_user(user=config.bot.get_user(dialogue_data.user_id), bp="NaN", region="NaN")

            if result is None:
                return [1, dialogue_data]

            elif "Similar Sign Up already exists" in result:
                dialogue_data.data.sign_up_error = result
                return [1, dialogue_data]

            else:
                dialogue_data.data.sign_up_error = result
                return [3, dialogue_data]

        else:
            await Storage.store_user(config.declined_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(config.contacted_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            await Storage.remove_user(config.remaining_leap_file_name, bot.get_user(dialogue_data.user_id), dialogue_data.data.role)
            return [2, dialogue_data]

    return evaluator

async def message_script_0():
    async def constructor(dialogue_data):
        iteration = "fifth"
        season_start = "1741460400"
        message = f'''
Hello again, as you are probably aware, the next season of PORC is about to begin!
As of now, you have been an active member of the PORC league, which will start its next season on **<t:{season_start}:F>**.
If you want to **continue being a part of PORC for the {iteration} season**, please react with ✅ to this message.
If you react with ❌ or do not react to this message, you will **not be entered** into the {iteration} season of PORC.
Thanks for participating in the last season, and we hope to see you around in the next one!

**Do you want to participate in the {iteration} season of PORC?**
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


async def construct(dialogue_data, index: int):

    return DialoguePlan(
        index,
        dialogue_data,
        [
            DialogueStep(
                await message_script_0(),  # would you like to sign up?
                "react",
                await completion_script_0()
            ),
            DialogueStep(
                await message_script_1(),  # sign up complete
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_2(),  # decline registered successfully
                "info",
                await completion_script_end()
            ),
            DialogueStep(
                await message_script_3(),  # error occurred
                "info",
                await completion_script_end()
            )
        ]
    )
