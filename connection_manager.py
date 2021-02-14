from fastapi import WebSocket
import json
from logger import logger

TAG = "connection_manager"


class ConnectionManager:
    def __init__(self):
        self.games = {}  # key: game_id, value game object
        self.user_game = {}  # key: String username, value gameid
        # key: username, value websocket object
        self.clients = {}

    async def connect(self, websocket: WebSocket, username):
        logger.info(TAG + f"\nUser {username} connected to new websocket")
        self.clients[username] = websocket

    def disconnect(self, username):
        logger.info(TAG + f"\nUser {username} disconnected")
        self.clients.pop(username)

    async def join_game(self, username, game_id):
        logger.info(TAG + f"\nexisting games are {self.games.keys()}")
        logger.info(TAG + f"\ngame id to join is {game_id}")

        if(game_id not in self.games.keys()):
            logger.info(TAG + "\ngame hasn't been created yet")
        elif(username in self.user_game.keys()):
            logger.info(TAG + "\nUser is already in a game")
        elif(not self.games[game_id].wait_reason == "waiting to join"):
            logger.info(TAG + "\nGame is not joinable anymore")
        else:
            logger.info(TAG + f"\nUser {username} is joining game {game_id}")
            self.user_game[username] = game_id
            await self.games[game_id].join(username)

    async def send_personal_message(self, message: str, username: str):
        logger.info(TAG + f"\nSending {message} to {username}.")
        await self.clients[username].send_text(message)

    async def send_users_in_game(self, message: str, game_id: int):
        logger.info(TAG + f"\nSending {message} to players in game {game_id}")
        for username in self.games[game_id].players:
            if not username.startswith("Bot"):
                await self.send_personal_message(message, username)

    async def broadcast(self, message: str):
        logger.info(TAG + f"\nBroadcasting message {message}.")
        for username in self.clients.keys():
            await self.send_personal_message(message, username)

    async def send_data(self, send_type, data, username):
        if(send_type == "Hand"):
            await self.send_personal_message(json.dumps(
                {"type": send_type,
                 "hand": data}),
                 username)
        elif(send_type == "PromptAction"):
            await self.send_personal_message(json.dumps(
                {"type": send_type,
                 "action": data["action"],
                 "play_validity": data["play_validity"]}),
                username)
        elif(send_type == "CreatedGameID"):
            await self.send_personal_message(json.dumps(
                {"type": send_type,
                 "game_id": data}),
                username)
        elif(send_type == "PlayerJoined"):
            players = self.games[data["game_id"]].players
            for i in range(len(players)):
                if players[i] and not players[i].startswith("Bot"):
                    await self.send_personal_message(
                        json.dumps(
                            {"type": "PlayerJoined",
                             "username": data["username"],
                             "playerIndex": data["playerIndex"],
                             "game_id": data["game_id"]
                             }
                            ),
                        players[i]
                        )
        elif(send_type == "game_ids"):
            games = []
            for gameID in self.games.keys():
                player1 = ""
                player2 = ""
                player3 = ""
                if len(self.games[gameID].players) > 0:
                    player1 = self.games[gameID].players[0]
                if len(self.games[gameID].players) > 1:
                    player2 = self.games[gameID].players[1]
                if len(self.games[gameID].players) > 2:
                    player3 = self.games[gameID].players[2]

                games.append({
                    "gameID": gameID,
                    "player1": player1,
                    "player2": player2,
                    "player3": player3,
                    })

            await self.send_personal_message(
                        json.dumps(
                            {"type": "game_ids",
                             "games": games}
                            ),
                        username
                        )
        elif(send_type == "BroadcastTrumpCard"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "card_val": data["card_val"]}),
                data["game_id"])
        elif(send_type == "PlayedCard1"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "card_val": data["card_val"],
                 "username": data['username'],
                 "marias": data["marias"]}),
                data["game_id"])
        elif(send_type == "PlayedCard2"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "card_val": data["card_val"],
                 "username": data['username'],
                 "marias": data["marias"]}),
                data["game_id"])
        elif(send_type == "PlayedCard3"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "card_val": data["card_val"],
                 "username": data['username'],
                 "marias": data["marias"]}),
                data["game_id"])
        elif(send_type == "EndHand"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "points0": data["points0"],
                 "points1": data["points1"],
                 "points2": data["points2"]}),
                data["game_id"])
        elif(send_type == "EndSet"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "winner": data["winner"],
                 "points0": data["points0"],
                 "points1": data["points1"],
                 "points2": data["points2"]}),
                data["game_id"])
        elif(send_type == "GameStart"):
            await self.send_users_in_game(json.dumps(
                {"type": send_type,
                 "player1": data["player1"],
                 "player2": data["player2"],
                 "player3": data["player3"],
                 "dealer": data["dealer"]}),
                data["game_id"])
        elif(send_type == "Reconnect"):
            await self.send_personal_message(json.dumps(
                {
                    "type": send_type,
                    "player1": data["player1"],
                    "player2": data["player2"],
                    "player3": data["player3"],
                    "dealer": data["dealer"],
                    "points0": data["points0"],
                    "points1": data["points1"],
                    "points2": data["points2"],
                    "game_id": data["game_id"],
                    "player_cards": data["player_cards"],
                    "hand": data["hand"],
                    "trump": data["trump"]
                 }),
                username
                )
        elif(send_type == "error"):
            await self.send_personal_message(json.dumps(
                {
                    "type": send_type,
                    "error_message": data["error_message"],
                 }),
                username
                )
        else:
            logger.infor(TAG + "case not matched")
