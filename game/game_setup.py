import asyncio
import random
import numpy as np
import warnings
from logger import logger
from game.utils import get_card, valid_plays
from param import BOT_THINK_TIME
from operator import itemgetter

TAG = "game_setup"


class Game:
    def __init__(self, manager):
        self.players = []

        self.player_cards = [[], [], []]
        self.points = [0, 0, 0]

        self.dealer = 0  # 0,1 or 2
        self.hand_starting_player = 1
        self.current_player = 1
        self.hand = [-1, -1, -1]
        self.game_id = None  # set by manager
        self.deck = []
        self.trump = None
        self.trump_card_value = None
        self.wait_for = None
        self.wait_reason = "waiting to join"
        self.play_validity = []
        self.manager = manager
        self.game_id
        self.marias = [False, False, False]

    async def join(self, username):
        if(not username):  # add a bot
            username = "Bot" + str(len(self.players))

        if(len(self.players) < 3):
            self.players.append(username)
            await self.manager.send_data(
                "PlayerJoined",
                {"username": username,
                 "playerIndex": len(self.players) - 1,
                 "game_id": self.game_id
                 },
                None)
        else:
            logger.info(TAG + "trying to join game with 3 players already")

    async def start_game(self):
        while len(self.players) < 3:  # add bots
            await self.join(None)

        await self.manager.send_data(
            "GameStart",
            {"player1": self.players[0],
             "player2": self.players[1],
             "player3": self.players[2],
             "dealer": self.dealer,
             "game_id": self.game_id},
            None)
        self.wait_for = self.players[(self.dealer + 1) % 3]
        await self.set_setup()

    async def set_setup(self):
        self.deck = [
            1,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
        ]
        random.shuffle(self.deck)
        self.player_cards = [[], [], []]
        self.points = [0, 0, 0]

        self.give_cards((self.dealer + 1) % 3, 7)
        self.give_cards((self.dealer + 2) % 3, 5)
        self.give_cards(self.dealer, 5)
        self.sort_hands()

        self.play_validity = [True for i in range(7)]
        self.wait_for = self.players[(self.dealer + 1) % 3]
        self.wait_reason = "trump_choice"

        for player in self.players:
            if(not player.startswith("Bot")):
                await self.show_hand(player)

        if self.wait_for.startswith("Bot"):
            await asyncio.sleep(BOT_THINK_TIME)
            await self.receive_trump_card_choice(-1)
        else:
            await self.manager.send_data("PromptAction",
                                         {"action": "Choose Trump card",
                                          "play_validity": self.play_validity},
                                         self.wait_for)

    def give_cards(self, player, card_amount):
        self.player_cards[player] = self.player_cards[player] + (
            self.deck[:card_amount])
        self.deck = self.deck[card_amount:]

    def sort_hands(self):
        for i in range(len(self.player_cards)):
            hand_details = []
            for card in self.player_cards[i]:
                card_details = get_card(card)
                if(card_details[0] == self.trump):
                    hand_details.append([4, card_details[1]])
                else:
                    hand_details.append([card_details[0], card_details[1]])

            hand_details = sorted(hand_details, key=itemgetter(1))
            hand_details = sorted(hand_details, key=itemgetter(0))

            for j in range(len(hand_details)-1, -1, -1):
                card_val = 0
                if hand_details[j][0] == 4:
                    card_val = card_val + 13*self.trump
                else:
                    card_val = card_val + 13*hand_details[j][0]

                if hand_details[j][1] == 13:  # king
                    card_val = card_val + 13
                elif hand_details[j][1] == 14:  # 10
                    card_val = card_val + 10
                elif hand_details[j][1] == 15:  # ace
                    card_val = card_val + 1
                else:
                    card_val = card_val + hand_details[j][1]

                self.player_cards[i][len(hand_details) - 1 - j] = card_val

    def remove_card_idx(self, player, card_idx):
        del self.player_cards[player][card_idx]

    def remove_card_val(self, player, card_value):
        self.player_cards[player].remove(card_value)

    async def receive_trump_card_choice(self, trump_card_idx):
        valid_indexes = [i for i, x in enumerate(self.play_validity) if x]
        if(trump_card_idx not in valid_indexes):
            trump_card_idx = random.choice(valid_indexes)
            warnings.warn(
                f"Invalid Choice, choosing randomly: {trump_card_idx}")

        self.trump_card_value = self.player_cards[
            (self.dealer + 1) % 3
            ][trump_card_idx]

        # 0-12 hearts, 13-25 diamond etc.
        self.trump = int((self.trump_card_value - 1) / 13)
        self.remove_card_idx((self.dealer + 1) % 3, trump_card_idx)

        self.give_cards((self.dealer + 1) % 3, 5)
        self.give_cards((self.dealer + 2) % 3, 5)
        self.give_cards(self.dealer, 5)
        self.sort_hands()

        for player in self.players:
            if not player.startswith("Bot"):
                await self.show_hand(player)

        self.wait_for = self.players[(self.dealer + 1) % 3]
        self.wait_reason = "talon_choice1"

        # valid_index any index that's not a 10 or Ace or trump color
        self.play_validity = [
            (
                get_card(
                    self.player_cards[
                        (self.dealer + 1) % 3
                        ][i]
                    )[1]
                not in [14, 15]
                and
                not
                get_card(
                    self.player_cards[
                        (self.dealer + 1) % 3
                        ][i]
                )[0] == self.trump
            )
            for i in range(11)]

        if self.wait_for.startswith("Bot"):
            await asyncio.sleep(BOT_THINK_TIME)
            await self.receive_talon_choice1(-1)
        else:
            await self.manager.send_data("PromptAction",
                                         {"action": "Choose Talon card",
                                          "play_validity": self.play_validity},
                                         self.wait_for)

    async def receive_talon_choice1(self, rmv1_idx):
        valid_indexes = [i for i, x in enumerate(self.play_validity) if x]
        if rmv1_idx not in valid_indexes:
            rmv1_idx = random.choice(valid_indexes)
            warnings.warn(f"Invalid Choice, choosing randomly: {rmv1_idx}")

        self.remove_card_idx((self.dealer + 1) % 3, rmv1_idx)
        self.wait_reason = "talon_choice2"
        # valid_index any index that's not a 10 or Ace or trump color
        self.play_validity = [
            (
                get_card(
                    self.player_cards[
                        (self.dealer + 1) % 3
                        ][i]
                    )[1]
                not in [14, 15]
                and
                not
                get_card(
                    self.player_cards[
                        (self.dealer + 1) % 3
                        ][i]
                )[0] == self.trump
            )
            for i in range(10)]

        if self.wait_for.startswith("Bot"):
            await asyncio.sleep(BOT_THINK_TIME)
            await self.receive_talon_choice2(-1)
        else:
            await self.manager.send_data("PromptAction",
                                         {"action": "Choose Talon card",
                                          "play_validity": self.play_validity},
                                         self.wait_for)

    async def receive_talon_choice2(self, rmv2_idx):
        valid_indexes = [i for i, x in enumerate(self.play_validity) if x]
        if rmv2_idx not in valid_indexes:
            rmv2_idx = random.choice(valid_indexes)
            warnings.warn(f"Invalid Choice, choosing randomly: {rmv2_idx}")

        # TODO: check removed not ace or ten
        self.remove_card_idx((self.dealer + 1) % 3, rmv2_idx)

        await self.manager.send_data("BroadcastTrumpCard",
                                     {"card_val": self.trump_card_value,
                                      "game_id": self.game_id},
                                     None)

        # add trump card to hand
        self.player_cards[(self.dealer + 1) % 3].append(self.trump_card_value)
        self.sort_hands()
        await self.init_hand()

    async def init_hand(self):
        player_1st = self.hand_starting_player
        self.current_player = player_1st
        self.play_validity = [True for i in range(
                len(self.player_cards[player_1st])
            )]
        self.wait_for = self.players[player_1st]
        self.wait_reason = "receive_play1"

        if(self.players[self.current_player].startswith("Bot")):
            await asyncio.sleep(BOT_THINK_TIME)
            await self.receive_play1(-1)
        else:
            await self.manager.send_data("PromptAction",
                                         {"action": "Play a card",
                                          "play_validity": self.play_validity},
                                         self.wait_for)

    async def receive_play1(self, play_index):
        valid_indexes = [i for i, x in enumerate(self.play_validity) if x]
        if play_index not in valid_indexes:
            play_index = random.choice(valid_indexes)
            warnings.warn(f"Invalid Choice, choosing randomly: {play_index}")

        card_1st = self.player_cards[self.current_player][play_index]

        # if played card is a queen, and player holds king of same colour
        if(card_1st % 13 == 12 and
           card_1st+1 in self.player_cards[self.current_player]):
            self.marias[self.current_player] = True

        username = self.players[self.current_player]
        self.hand[self.current_player] = card_1st
        self.remove_card_val(self.current_player, card_1st)

        if(not self.players[self.current_player].startswith("Bot")):
            await self.show_hand(self.players[self.current_player])

        await self.manager.send_data("PlayedCard1",
                                     {"card_val": card_1st,
                                      "username": username,
                                      "game_id": self.game_id,
                                      "marias": self.marias[
                                          self.current_player
                                          ]},
                                     None)

        self.current_player = (self.current_player + 1) % 3

        self.play_validity = valid_plays(
            self.player_cards[self.current_player],
            card_1st,
            None,
            self.trump)

        self.wait_for = self.players[self.current_player]
        self.wait_reason = "receive_play2"

        if(self.players[self.current_player].startswith("Bot")):
            await asyncio.sleep(BOT_THINK_TIME)
            await self.receive_play2(-1)
        else:
            await self.manager.send_data(
                "PromptAction",
                {"action": "Play a card",
                 "play_validity": self.play_validity},
                self.wait_for)

    async def receive_play2(self, play_index):
        valid_indexes = [i for i, x in enumerate(self.play_validity) if x]
        if play_index not in valid_indexes:
            play_index = random.choice(valid_indexes)
            warnings.warn(f"Invalid Choice, choosing randomly: {play_index}")

        card_1st = self.hand[(self.current_player + 2) % 3]
        card_2nd = self.player_cards[self.current_player][play_index]
        # if played card is a queen, and player holds king of same colour
        if(card_2nd % 13 == 12 and
           card_2nd+1 in self.player_cards[self.current_player]):
            self.marias[self.current_player] = True

        username = self.players[self.current_player]

        self.hand[self.current_player] = card_2nd
        self.remove_card_val(self.current_player, card_2nd)

        if(not self.players[self.current_player].startswith("Bot")):
            await self.show_hand(self.players[self.current_player])

        await self.manager.send_data("PlayedCard2",
                                     {"card_val": card_2nd,
                                      "username": username,
                                      "game_id": self.game_id,
                                      "marias": self.marias[
                                          self.current_player
                                          ]},
                                     None)

        self.current_player = (self.current_player + 1) % 3

        self.play_validity = valid_plays(
            self.player_cards[self.current_player],
            card_1st,
            card_2nd,
            self.trump)

        self.wait_for = self.players[self.current_player]
        self.wait_reason = "receive_play3"

        if(self.players[self.current_player].startswith("Bot")):
            await asyncio.sleep(BOT_THINK_TIME)
            await self.receive_play3(-1)
        else:
            await self.manager.send_data(
                "PromptAction",
                {"action": "Play a card",
                 "play_validity": self.play_validity},
                self.wait_for)

    async def receive_play3(self, play_index):
        valid_indexes = [i for i, x in enumerate(self.play_validity) if x]
        if play_index not in valid_indexes:
            play_index = random.choice(valid_indexes)
            warnings.warn(f"Invalid Choice, choosing randomly: {play_index}")

        card_3rd = self.player_cards[self.current_player][play_index]
        # if played card is a queen, and player holds king of same colour
        if(card_3rd % 13 == 12 and
           card_3rd+1 in self.player_cards[self.current_player]):
            self.marias[self.current_player] = True
        username = self.players[self.current_player]

        self.hand[self.current_player] = card_3rd
        self.remove_card_val(self.current_player, card_3rd)

        if(not self.players[self.current_player].startswith("Bot")):
            await self.show_hand(self.players[self.current_player])

        await self.manager.send_data("PlayedCard3",
                                     {"card_val": card_3rd,
                                      "username": username,
                                      "game_id": self.game_id,
                                      "marias": self.marias[
                                          self.current_player
                                          ]},
                                     None)

        self.current_player = (self.current_player + 1) % 3
        await self.finalize_hand()

    async def show_hand(self, username):
        idx = self.players.index(username)
        await self.manager.send_data("Hand",
                                     self.player_cards[idx],
                                     username)

    async def finalize_hand(self):
        card0 = get_card(self.hand[self.hand_starting_player])
        card1 = get_card(self.hand[(self.hand_starting_player + 1) % 3])
        card2 = get_card(self.hand[(self.hand_starting_player + 2) % 3])
        new_points = 0

        marias_played = np.where(self.marias)[0]

        for marias_index in marias_played:
            if get_card(self.hand[marias_index])[0] == self.trump:
                self.points[marias_index] = self.points[
                    marias_index] + 40
            else:
                self.points[marias_index] = self.points[
                    marias_index] + 20

        # card[0] is the card color, card[1] the card strength (Ace>10>King)
        # if card1 beats card0
        if (card1[0] == card0[0]
                and card1[1] > card0[1]) or (card1[0] == self.trump
                                             and not card0[0] == self.trump):
            # and card2 beats card1
            if ((card2[0] == self.trump and not card1[0] == self.trump) or
               (card2[0] == card1[0] and card2[1] > card1[1])):
                self.hand_starting_player = (self.hand_starting_player + 2) % 3
            else:
                self.hand_starting_player = (self.hand_starting_player + 1) % 3
        # if card 2 beats card0
        elif ((card2[0] == card0[0] and card2[1] > card0[1]) or
              (card2[0] == self.trump and not card0[0] == self.trump)):
            self.hand_starting_player = (self.hand_starting_player + 2) % 3

        # else do nothing: card0 won -> same hand_starting_player

        # for every card that is a 10 or ace, add 10 points
        if card0[1] == 14 or card0[1] == 15:
            new_points = new_points + 10
        if card1[1] == 14 or card1[1] == 15:
            new_points = new_points + 10
        if card2[1] == 14 or card2[1] == 15:
            new_points = new_points + 10

        self.points[self.hand_starting_player] = (
            self.points[self.hand_starting_player] + new_points)
        self.hand = [-1, -1, -1]
        self.marias = [False, False, False]

        await self.manager.send_data("EndHand",
                                     {
                                      "points0": self.points[0],
                                      "points1": self.points[1],
                                      "points2": self.points[2],
                                      "game_id": self.game_id
                                      },
                                     None)

        if len(self.player_cards[0]) == 0:
            self.points[self.hand_starting_player] = (
                self.points[self.hand_starting_player] + 10)

            if np.argmax([self.points[self.dealer] + self.points[
                (self.dealer + 2) % 3
                ],
                self.points[(self.dealer + 1) % 3]
                    ]) == 0:
                winner = (self.players[self.dealer] + " and " +
                          self.players[(self.dealer + 2) % 3])
            else:
                winner = self.players[(self.dealer + 1) % 3]

            await self.manager.send_data(
                "EndSet",
                {"winner": winner,
                 "points0": self.points[0],
                 "points1": self.points[1],
                 "points2": self.points[2],
                 "game_id": self.game_id
                 },
                None
                )

            self.dealer = (self.dealer + 1) % 3

            await self.manager.send_data(
                "GameStart",
                {"player1": self.players[0],
                 "player2": self.players[1],
                 "player3": self.players[2],
                 "dealer": self.dealer,
                 "game_id": self.game_id
                 },
                None)

            self.hand_starting_player = (self.dealer + 1) % 3
            self.current_player = (self.dealer + 1) % 3
            await self.set_setup()
        else:
            await self.init_hand()

    async def reconnect(self, username):
        await self.manager.send_data(
                "Reconnect",
                {
                    "player1": self.players[0],
                    "player2": self.players[1],
                    "player3": self.players[2],
                    "dealer": self.dealer,
                    "points0": self.points[0],
                    "points1": self.points[1],
                    "points2": self.points[2],
                    "game_id": self.game_id,
                    "player_cards": self.player_cards[self.players.index(
                        username)],
                    "hand": self.hand,
                    "trump": self.trump_card_value
                 },
                username
                )

        if username == self.wait_for:
            await self.manager.send_data(
                "PromptAction",
                {
                    "action": "Your turn",
                    "play_validity": self.play_validity},
                username)

    def leave_game(self, username):
        index = self.players.index(username)
        self.players[index] == "Bot" + str(index)
