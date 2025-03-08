import discord
from discord.ext import tasks, commands
import DiscordModule as Communication
import config as Config
import SecurityModule
import StorageModule as Storage
import ServerCommunicationModule as API
from colorama import Fore, Style
import json
import os

import DialogueRoutes


class DialoguePlan:
    def __init__(self, index, dialogue_data, steps):
        self.index = index
        self.dialogue_data = dialogue_data
        self.steps = steps

    async def check(self):
        # print(f"checking dialogue plan, current step: {self.index}")
        current_step = self.steps[self.index]
        completion = await current_step.check_completion(dialogue_data=self.dialogue_data)
        self.dialogue_data = completion[1]
        next_index = completion[0]
        # print(f"next index {next_index}")
        if next_index >= 0 and next_index is not self.index:
            await self.next(target_index=next_index)
            return True

        else:
            return False

    async def next(self, target_index):
        self.index = target_index
        if target_index == 600:
            print("A dialogue has reached its end")

        elif self.steps[target_index].completion_condition == "react":
            await Communication.send_prompt_message(Config.bot.get_user(self.dialogue_data.user_id), await self.steps[target_index].get_message(self.dialogue_data))

        else:
            await Communication.send_info_message(Config.bot.get_user(self.dialogue_data.user_id), await self.steps[target_index].get_message(self.dialogue_data))

    def getBuilder(self):
        return DialogueBuilder(dialogue_data=self.dialogue_data, current_index=self.index)




class DialogueStep:
    def __init__(self, message_script, completion_condition, completion_script):
        if completion_condition == "response" or completion_condition == "react" or completion_condition == "info":
            self.message_script = message_script
            self.completion_condition = completion_condition
            self.completion_script = completion_script
        else:
            raise ValueError("completion condition must have one of the following values: 'response', 'react' or 'info'")

    async def check_completion(self, dialogue_data):
        # print("checking step completion")

        if self.completion_condition == "response":
            # print("checking for 'response' type")
            response = await Communication.check_response(Config.bot.get_user(dialogue_data.user_id), await self.get_message(dialogue_data=dialogue_data))
            if len(response) > 0:
                return await self.completion_script(dialogue_data=dialogue_data, response=response[0][0])

            else:
                print("no response found")
                return [-1, dialogue_data]

        elif self.completion_condition == "react":
            # print("checking for 'react' type")
            reactions = await Communication.check_reaction(Config.bot.get_user(dialogue_data.user_id), await self.get_message(dialogue_data=dialogue_data))
            approval = False
            decline = False
            for reaction in reactions:

                if reaction == Communication.accept_emoji:
                    approval = True

                if reaction == Communication.decline_emoji:
                    decline = True

            if approval and not decline:
                return await self.completion_script(dialogue_data=dialogue_data, approval=True, no_resp=False)

            elif decline and not approval:
                return await self.completion_script(dialogue_data=dialogue_data, approval=False, no_resp=False)

            else:
                return await self.completion_script(dialogue_data=dialogue_data, approval=False, no_resp=True)

        elif self.completion_condition == "info":
            # print("checking for 'info' type")
            return await self.completion_script(dialogue_data=dialogue_data)

        else:
            return [-1, dialogue_data]  # in case nothing returns -1; integer represents index of next dialogue step, negative means remain on current step, 600 means terminate

    async def get_message(self, dialogue_data):
        return await self.message_script(dialogue_data)



class DialogueData:
    def __init__(self, kind, user_id, data):
        if kind == "SeasonLeap":
            if not isinstance(data, LeapData):
                raise ValueError("data type does not match DialogueData kind")

        elif kind == "SeasonInvite":
            if not isinstance(data, InviteData):
                raise ValueError("data type does not match DialogueData kind")

        elif kind == "MatchRequest":
            if not isinstance(data, MatchRequestData):
                raise ValueError("data type does not match DialogueData kind")

        else:
            raise ValueError("kind needs to be one of the following: 'SeasonLeap', 'SeasonInvite'")

        self.kind = kind
        self.user_id = user_id
        self.data = data

    def serialize(self):
        return {
            "kind": self.kind,
            "user_id": self.user_id,
            "data": self.data.serialize()
        }

    def deserialize(data_to_desirialize):
        kind = data_to_desirialize["kind"]
        user_id = data_to_desirialize["user_id"]

        if kind == "SeasonLeap":
            data = LeapData.deserialize(data_to_desirialize["data"])

        elif kind == "SeasonInvite":
            data = InviteData.deserialize(data_to_desirialize["data"])

        elif kind == "MatchRequest":
            data = MatchRequestData.deserialize(data_to_desirialize["data"])

        else:
            raise ValueError("kind needs to be one of the following: 'SeasonLeap', 'SeasonInvite', 'MatchRequest'")

        return DialogueData (
            kind=kind,
            user_id=user_id,
            data=data
        )


class LeapData:
    def __init__(self, role, sign_up_error):
        self.role = role
        self.sign_up_error = sign_up_error

    def serialize(self):
        return {
            "role": self.role,
            "sign_up_error": self.sign_up_error
        }

    def deserialize(data):
        return LeapData(
            role=data["role"],
            sign_up_error=data["sign_up_error"]
        )


class InviteData:
    def __init__(self, bp, sign_up_error):
        self.bp = bp
        self.sign_up_error = sign_up_error

    def serialize(self):
        return {
            "bp": self.bp,
            "sign_up_error": self.sign_up_error
        }

    def deserialize(data):
        return InviteData(
            bp=data["bp"],
            sign_up_error=data["sign_up_error"]
        )


class MatchRequestData:
    def __init__(self, challenger_id, opponent_id, start_timestamp, league, event_id):
        self.challenger_id = challenger_id
        self.opponent_id = opponent_id
        self.start_timestamp = start_timestamp
        self.league = league
        self.event_id = event_id

    def serialize(self):
        return {
            "challenger_id": self.challenger_id,
            "event_id": self.event_id,
            "league": self.league,
            "start_timestamp": self.start_timestamp,
            "opponent_id": self.opponent_id,
        }

    def deserialize(data):
        return MatchRequestData(
            challenger_id=data["challenger_id"],
            event_id=data["event_id"],
            league=data["league"],
            start_timestamp=data["start_timestamp"],
            opponent_id=data["opponent_id"]
        )


class DialogueBuilder:
    def __init__(self, dialogue_data, current_index):
        self.dialogue_data = dialogue_data
        self.current_index = current_index

    def serialize(self):
        return {
            "dialogue_data": self.dialogue_data.serialize(),
            "current_index": self.current_index,
        }

    def deserialize(data):
        return DialogueBuilder(
            dialogue_data=DialogueData.deserialize(data["dialogue_data"]),
            current_index=data["current_index"]
        )

    async def build(self):

        if self.dialogue_data.kind == "SeasonLeap":
            from DialogueRoutes.SeasonLeap import construct as leap_construct
            return await leap_construct(dialogue_data=self.dialogue_data, index=self.current_index)

        if self.dialogue_data.kind == "SeasonInvite":
            from DialogueRoutes.SeasonInvite import construct as invite_construct
            return await invite_construct(dialogue_data=self.dialogue_data, index=self.current_index)

        if self.dialogue_data.kind == "MatchRequest":
            from DialogueRoutes.MatchRequest import construct as match_request_construct
            return await match_request_construct(dialogue_data=self.dialogue_data, index=self.current_index)

        if self.dialogue_data.kind == "":
            return print("imported building function")


class DialogueInitiator:

    def __init__(self):
        self = self

    async def initiate_SeasonLeap(self, user_id, role):

        builder = DialogueBuilder(
            dialogue_data=DialogueData(
                kind="SeasonLeap",
                user_id=user_id,
                data=LeapData(
                    role=role,
                    sign_up_error=None
                )
            ),
            current_index=0
        )

        plan = await builder.build()
        message = await plan.steps[0].get_message(plan.dialogue_data)

        if plan.steps[0].completion_condition == "react":
            await Communication.send_prompt_message(Config.bot.get_user(user_id), message)

        else:
            await Communication.send_info_message(Config.bot.get_user(user_id), message)

        await Storage.store_user(Config.contacted_leap_file_name, Config.bot.get_user(user_id), role)

        return builder

    async def initiate_SeasonInvite(self, user_id):

        builder = DialogueBuilder(
            dialogue_data=DialogueData(
                kind="SeasonInvite",
                user_id=user_id,
                data=InviteData(
                    bp="NaN",
                    sign_up_error=None
                )
            ),
            current_index=0
        )

        plan = await builder.build()
        message = await plan.steps[0].get_message(plan.dialogue_data)

        if plan.steps[0].completion_condition == "react":
            await Communication.send_prompt_message(Config.bot.get_user(user_id), message)

        else:
            await Communication.send_info_message(Config.bot.get_user(user_id), message)

        await Storage.store_user(Config.contacted_invite_file_name, Config.bot.get_user(user_id), "NaN")

        return builder

    async def initiate_MatchRequest(self, user_id, challenger_id, opponent_id, start_timestamp, league):

        builder = DialogueBuilder(
            dialogue_data=DialogueData(
                kind="MatchRequest",
                user_id=user_id,
                data=MatchRequestData(
                    challenger_id=challenger_id,
                    opponent_id=opponent_id,
                    start_timestamp=start_timestamp,
                    league=league,
                    event_id=None
                )
            ),
            current_index=0
        )

        plan = await builder.build()
        message = await plan.steps[0].get_message(plan.dialogue_data)

        if plan.steps[0].completion_condition == "react":
            await Communication.send_prompt_message(Config.bot.get_user(user_id), message)

        else:
            await Communication.send_info_message(Config.bot.get_user(user_id), message)

        return builder
